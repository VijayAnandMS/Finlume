import os, shutil, tempfile, uuid, json, time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.models import User, ImportSession, ImportRecord, Transaction, ImportAuditLog
from app.routes.auth import get_current_user
from app.schemas.schemas import ImportSessionOut, ImportRecordOut, ImportAuditLogOut

from app.services.imports.validator import FileValidator
from app.services.imports.parser_factory import ParserFactory
from app.services.imports.duplicate_detector import DuplicateDetector
from app.services.imports.categorizer import TransactionCategorizer
from app.services.imports.exceptions import (
    UnsupportedFileException, CorruptedFileException, 
    MissingColumnsException, ParsingFailureException
)

router = APIRouter(prefix="/api/import", tags=["import"])

# ----------------- SCHEMAS -----------------
class UploadResponse(BaseModel):
    session_id: str
    filename: str
    total_parsed: int
    warnings: List[str]

class RecordUpdate(BaseModel):
    category: Optional[str] = None
    status: Optional[str] = None

class BatchPreviewUpdate(BaseModel):
    updates: Dict[str, RecordUpdate]

# ----------------- HELPERS -----------------
def log_audit(db: Session, session_id: str, user_id: int, action: str, resource: str = None, details: str = None):
    log = ImportAuditLog(
        session_id=session_id, user_id=user_id, action=action, 
        resource=resource, details=details
    )
    db.add(log)
    db.commit()

# ----------------- UPLOAD ENDPOINT -----------------
@router.post("/upload", response_model=UploadResponse)
async def upload_statement(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    start_time = time.time()
    filename = os.path.basename(file.filename) if file.filename else "unknown"
    ext = os.path.splitext(filename)[1].lower()
    
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    import_session = None
    try:
        with os.fdopen(fd, 'wb') as f: shutil.copyfileobj(file.file, f)
            
        FileValidator.validate(temp_path)
            
        parser = ParserFactory.get_parser(temp_path)
        transactions = parser.parse(temp_path)
        if not transactions:
            raise HTTPException(status_code=422, detail="No valid transactions.")

        cat = TransactionCategorizer(user_id=current_user.id)
        transactions = cat.categorize_batch(transactions)
        
        dup = DuplicateDetector(db, user_id=current_user.id)
        transactions = dup.process_batch(transactions)
        
        duplicates_found = sum(1 for tx in transactions if tx.get('Duplicate Status') == 'EXACT_DUPLICATE')
        
        import_session = ImportSession(
            user_id=current_user.id, filename=filename, status="MAPPED",
            total_records=len(transactions), duplicates_found=duplicates_found,
            duration_ms=int((time.time() - start_time)*1000)
        )
        db.add(import_session)
        db.commit()
        db.refresh(import_session)
        
        log_audit(db, import_session.id, current_user.id, "Upload Started", filename, "Initiating ETL pipeline")
        
        records_to_insert = []
        for tx in transactions:
            is_dup = (tx.get('Duplicate Status') == 'EXACT_DUPLICATE')
            cat_name = tx.get('Category')
            rec_status = "DISCARDED" if is_dup else "STAGED"
            date_obj = datetime.strptime(tx.get("Date"), "%Y-%m-%d").date() if tx.get("Date") else None
            
            rec = ImportRecord(
                session_id=import_session.id, raw_data=json.dumps(tx), parsed_amount=float(tx.get("Amount", 0.0)),
                parsed_date=date_obj, parsed_merchant=str(tx.get("Description", "")), 
                ai_category_suggestion=cat_name, is_duplicate=is_dup, status=rec_status
            )
            records_to_insert.append(rec)
            
        db.add_all(records_to_insert)
        db.commit()
        
        log_audit(db, import_session.id, current_user.id, "Preview Generated", None, f"Processed {len(transactions)} txs")
        
    except HTTPException as e:
        if import_session:
             log_audit(db, import_session.id, current_user.id, "Validation Failed", filename, str(e.detail))
             import_session.status = "FAILED"
             db.commit()
        raise e
    except UnsupportedFileException as e:
        if import_session:
             log_audit(db, import_session.id, current_user.id, "Validation Failed", filename, str(e))
             import_session.status = "FAILED"
             db.commit()
        raise HTTPException(status_code=415, detail=str(e))
    except MissingColumnsException as e:
        if import_session:
             log_audit(db, import_session.id, current_user.id, "Validation Failed", filename, str(e))
             import_session.status = "FAILED"
             db.commit()
        raise HTTPException(status_code=422, detail=str(e))
    except (CorruptedFileException, ParsingFailureException) as e:
        if import_session:
             log_audit(db, import_session.id, current_user.id, "Validation Failed", filename, str(e))
             import_session.status = "FAILED"
             db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if import_session:
             log_audit(db, import_session.id, current_user.id, "Validation Failed", filename, str(e))
             import_session.status = "FAILED"
             db.commit()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()
        if os.path.exists(temp_path): os.remove(temp_path)
            
    return UploadResponse(session_id=import_session.id, filename=filename, total_parsed=len(transactions), warnings=[])

# ----------------- STANDARD PREVIEW ENDPOINTS -----------------
@router.get("/{session_id}", response_model=ImportSessionOut)
def get_import_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    return si

@router.get("/{session_id}/preview", response_model=List[ImportRecordOut])
def get_import_preview(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    return db.query(ImportRecord).filter(ImportRecord.session_id == si.id).all()

@router.patch("/{session_id}/preview")
def update_preview_batch(session_id: str, payload: BatchPreviewUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    records = db.query(ImportRecord).filter(ImportRecord.session_id == si.id).all()
    record_map = {r.id: r for r in records}
    
    audit_events = []
    for rid, update_data in payload.updates.items():
        if rid in record_map:
            if update_data.category and record_map[rid].ai_category_suggestion != update_data.category:
                audit_events.append(ImportAuditLog(session_id=si.id, user_id=current_user.id, action="Category Modified", resource=rid, details=f"Changed to {update_data.category}"))
                record_map[rid].ai_category_suggestion = update_data.category
            if update_data.status and record_map[rid].status != update_data.status:
                record_map[rid].status = update_data.status
                action = "Transaction Excluded" if update_data.status == "DISCARDED" else "Transaction Included"
                audit_events.append(ImportAuditLog(session_id=si.id, user_id=current_user.id, action=action, resource=rid, details="Status updated"))
                
    db.add_all(audit_events)
    db.commit()
    return {"status": "success"}

@router.post("/{session_id}/confirm")
def confirm_import(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    
    start_time = time.time()
    records = db.query(ImportRecord).filter(ImportRecord.session_id == si.id).all()
    new_txs, skipped, manual = [], 0, 0
    for rec in records:
        if rec.status == "DISCARDED":
            skipped += 1
            continue
        # Check if manual was required via raw JSON embedding
        tx_data = json.loads(rec.raw_data)
        if tx_data.get("category_source") == "MANUAL_REQUIRED": manual += 1
            
        tx_type = "income" if rec.ai_category_suggestion == "Salary" else "expense"
        new_txs.append(Transaction(
            user_id=current_user.id, amount=abs(rec.parsed_amount) if rec.parsed_amount is not None else 0.0, transaction_date=rec.parsed_date,
            transaction_type=tx_type,
            description=rec.parsed_merchant, merchant=rec.parsed_merchant,
            category=rec.ai_category_suggestion or "Miscellaneous"
        ))
        rec.status = "IMPORTED"
        
    db.add_all(new_txs)
    si.status = "COMPLETED"
    si.imported_count = len(new_txs)
    si.skipped_count = skipped
    si.manual_reviews_count = manual
    si.duration_ms += int((time.time() - start_time)*1000)
    
    log_audit(db, si.id, current_user.id, "Import Confirmed", None, f"Imported {len(new_txs)}, Skipped {skipped}")
    return {"message": "Success", "imported": len(new_txs)}

@router.delete("/{session_id}", status_code=204)
def cancel_import_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    db.delete(si)
    db.commit()
    return None

# ----------------- PHASE 16.8 HISTORY & AUDIT ENDPOINTS -----------------
@router.get("/history/list", response_model=List[ImportSessionOut])
def get_import_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Returns history tracking cleanly avoiding heavy paginations explicitly initially
    return db.query(ImportSession).filter(ImportSession.user_id == current_user.id).order_by(ImportSession.created_at.desc()).all()

@router.get("/history/{session_id}", response_model=ImportSessionOut)
def get_import_history_details(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    return si

@router.get("/history/{session_id}/audit", response_model=List[ImportAuditLogOut])
def get_import_audit_timeline(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    si = db.query(ImportSession).filter(ImportSession.id == session_id, ImportSession.user_id == current_user.id).first()
    if not si: raise HTTPException(status_code=404, detail="Session not found")
    return db.query(ImportAuditLog).filter(ImportAuditLog.session_id == si.id).order_by(ImportAuditLog.timestamp.asc()).all()