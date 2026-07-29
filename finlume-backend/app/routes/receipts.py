import os
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.models import User, ReceiptSession, OCRResult, ParsedReceipt, ReceiptIntelligence
from app.routes.auth import get_current_user
from app.schemas.schemas import OCRResultOut, ParsedReceiptOut, ReceiptIntelligenceOut
from app.services.receipts.upload_service import ReceiptUploadService
from app.services.receipts.providers.azure_provider import AzureOCRProvider
from app.services.receipts.parser.parser import ReceiptParser
from app.services.receipts.intelligence.intelligence_service import ReceiptIntelligenceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/receipts", tags=["receipts"])

class UploadReceiptResponse(BaseModel):
    receipt_session_id: str
    filename: str
    storage_url: str

class ReceiptSessionOut(BaseModel):
    id: str
    filename: str
    storage_url: str
    status: str
    
    class Config:
        orm_mode = True

@router.post("/upload", response_model=UploadReceiptResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload_service = ReceiptUploadService()
    try:
        result = upload_service.process_upload(file, current_user.id)
        
        rs = ReceiptSession(
            user_id=current_user.id,
            filename=result["filename"],
            storage_url=result["storage_url"],
            status="UPLOADED"
        )
        db.add(rs)
        db.commit()
        db.refresh(rs)
        
        return {
            "receipt_session_id": rs.id,
            "filename": rs.filename,
            "storage_url": rs.storage_url
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
@router.get("/{receipt_session_id}", response_model=ReceiptSessionOut)
def get_receipt(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    return rs

@router.delete("/{receipt_session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    
    upload_service = ReceiptUploadService()
    filename_target = os.path.basename(rs.storage_url)
    upload_service.storage.delete(filename_target)
    
    db.delete(rs)
    db.commit()
    return None

# --- OCR ENGINE PIPELINE (PHASE 17.2) ---

@router.post("/{receipt_session_id}/ocr", response_model=OCRResultOut)
def process_receipt_ocr(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    if rs.status in ["OCR_PROCESSING"]:
        raise HTTPException(status_code=409, detail="Receipt is already processing")
        
    rs.status = "OCR_PROCESSING"
    db.commit()
    
    try:
        # Abstracted Execution Call
        ocr_provider = AzureOCRProvider()
        final_path = rs.storage_url 
        
        provider_result = ocr_provider.extract_receipt(final_path)
        
        errors = provider_result.get("errors", [])
        if errors:
            rs.status = "FAILED"
        else:
            rs.status = "COMPLETED"
            
        ocr = OCRResult(
            receipt_session_id=rs.id,
            raw_text=provider_result.get("raw_text", ""),
            confidence_score=provider_result.get("confidence", 0.0),
            detected_fields=json.dumps(provider_result.get("detected_fields", {})),
            bounding_regions=json.dumps(provider_result.get("bounding_regions", {})),
            processing_time_ms=provider_result.get("processing_time_ms", 0),
            warnings=json.dumps(provider_result.get("warnings", [])),
            errors=json.dumps(errors)
        )
        db.add(ocr)
        db.commit()
        db.refresh(ocr)
        
        return ocr

    except Exception as e:
        logger.error(f"Internal OCR Parsing Error: {e}")
        rs.status = "FAILED"
        db.commit()
        # Sanitized error avoiding explicit stack traces globally
        raise HTTPException(status_code=500, detail="Internal OCR API Failure")

@router.get("/{receipt_session_id}/ocr", response_model=OCRResultOut)
def get_receipt_ocr_result(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    
    ocr = db.query(OCRResult).filter(OCRResult.receipt_session_id == rs.id).order_by(OCRResult.id.desc()).first()
    
    if not ocr:
        raise HTTPException(status_code=404, detail="No OCR bounds processed yet")
        
    return ocr

# --- PARSING ENGINE (PHASE 17.3) ---

@router.post("/{receipt_session_id}/parse", response_model=ParsedReceiptOut)
def execute_receipt_parsing(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    
    ocr = db.query(OCRResult).filter(OCRResult.receipt_session_id == rs.id).order_by(OCRResult.id.desc()).first()
    if not ocr: raise HTTPException(status_code=400, detail="Cannot parse: No OCR result available")
    
    try:
        detected_fields = json.loads(ocr.detected_fields)
        parsed_data = ReceiptParser.parse_ocr_result(detected_fields)
        
        pr = ParsedReceipt(
            receipt_session_id=rs.id,
            merchant_name=parsed_data.get("merchant_name"),
            transaction_date=parsed_data.get("transaction_date"),
            subtotal=parsed_data.get("subtotal"),
            tax=parsed_data.get("tax"),
            total=parsed_data.get("total"),
            currency=parsed_data.get("currency"),
            warnings=json.dumps(parsed_data.get("warnings", []))
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)
        return pr
    except Exception as e:
        logger.error(f"Internal Parser fault: {e}")
        raise HTTPException(status_code=500, detail="Internal parsing execution failure securely caught.")

@router.get("/{receipt_session_id}/parsed", response_model=ParsedReceiptOut)
def get_parsed_receipt(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    
    pr = db.query(ParsedReceipt).filter(ParsedReceipt.receipt_session_id == rs.id).order_by(ParsedReceipt.id.desc()).first()
    if not pr: raise HTTPException(status_code=404, detail="No parsed limits mapping structurally")
    return pr

# --- AI INTELLIGENCE ENGINE (PHASE 17.4) ---

@router.post("/{receipt_session_id}/intelligence", response_model=ReceiptIntelligenceOut)
def execute_receipt_intelligence(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    
    pr = db.query(ParsedReceipt).filter(ParsedReceipt.receipt_session_id == rs.id).order_by(ParsedReceipt.id.desc()).first()
    if not pr: raise HTTPException(status_code=400, detail="Cannot apply Intelligence without Parsed Data")
    
    ocr = db.query(OCRResult).filter(OCRResult.receipt_session_id == rs.id).order_by(OCRResult.id.desc()).first()
    if not ocr: raise HTTPException(status_code=400, detail="Cannot apply Intelligence without OCR Confidence Data")
    
    try:
        parsed_dict = {
            "merchant_name": pr.merchant_name,
            "transaction_date": pr.transaction_date,
            "subtotal": pr.subtotal,
            "tax": pr.tax,
            "total": pr.total,
            "currency": pr.currency
        }
        
        intel_res = ReceiptIntelligenceService.enrich_receipt(parsed_dict, ocr.confidence_score, current_user.id)
        
        ri = ReceiptIntelligence(
            receipt_session_id=rs.id,
            predicted_category=intel_res.get("predicted_category"),
            field_corrections=json.dumps(intel_res.get("field_corrections", {})),
            overall_confidence=intel_res.get("overall_confidence", 0.0),
            requires_manual_review=intel_res.get("requires_manual_review", True),
            uncertainty_reasons=json.dumps(intel_res.get("uncertainty_reasons", []))
        )
        db.add(ri)
        db.commit()
        db.refresh(ri)
        return ri
    except Exception as e:
        logger.error(f"AI Failure securely mapped cleanly: {e}")
        raise HTTPException(status_code=500, detail="Internal Intelligence execution safely suppressed")

@router.get("/{receipt_session_id}/intelligence", response_model=ReceiptIntelligenceOut)
def get_receipt_intelligence(
    receipt_session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rs = db.query(ReceiptSession).filter(
        ReceiptSession.id == receipt_session_id, 
        ReceiptSession.user_id == current_user.id
    ).first()
    if not rs: raise HTTPException(status_code=404, detail="Receipt Session not found")
    
    ri = db.query(ReceiptIntelligence).filter(ReceiptIntelligence.receipt_session_id == rs.id).order_by(ReceiptIntelligence.id.desc()).first()
    if not ri: raise HTTPException(status_code=404, detail="No intelligence bounds processed natively")
    return ri
