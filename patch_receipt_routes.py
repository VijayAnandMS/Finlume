import os

models_path = "c:\\Vijay\\Projects\\Finlume\\finlume-backend\\app\\models\\models.py"

with open(models_path, "r") as f:
    content = f.read()

if "class ReceiptSession(Base):" not in content:
    receipt_mod = """
class ReceiptSession(Base):
    __tablename__ = "receipt_sessions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)
    status = Column(String, default="UPLOADED") # UPLOADED, OCR_PROCESSING, COMPLETED, FAILED
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
"""
    content += "\\n" + receipt_mod
    with open(models_path, "w") as f:
        f.write(content)
        
main_path = "c:\\Vijay\\Projects\\Finlume\\finlume-backend\\app\\main.py"
with open(main_path, "r") as f:
    main_content = f.read()

if "from app.routes import receipts" not in main_content:
    main_content = main_content.replace(
        "from app.routes import auth, transactions, dashboard, limits, agents, imports",
        "from app.routes import auth, transactions, dashboard, limits, agents, imports, receipts"
    )
    main_content = main_content.replace(
        "app.include_router(imports.router)",
        "app.include_router(imports.router)\\napp.include_router(receipts.router)"
    )
    with open(main_path, "w") as f:
        f.write(main_content)

print("Backend integrations patched natively.")
