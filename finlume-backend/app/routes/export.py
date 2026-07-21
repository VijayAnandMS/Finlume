from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.models import User, Transaction
from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter(prefix="/api/export", tags=["Reports"])

@router.get("/transactions.csv", summary="Generate CSV Export")
def export_transactions_csv(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Exports personal transaction logs into a standard CSV blob suitable for Excel manipulation."""
    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).order_by(Transaction.date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Header
    writer.writerow(['ID', 'Type', 'Category', 'Amount', 'Date'])
    
    for t in txs:
        writer.writerow([t.id, t.type.upper(), t.category, t.amount, t.date])
        
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=finlume_transactions.csv"}
    )
