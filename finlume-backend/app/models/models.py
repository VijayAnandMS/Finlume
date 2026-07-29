from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True) # made true for backward compatibility
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True) # nullable for old users
    phone_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    
    is_email_verified = Column(Boolean, default=False)
    profile_completed = Column(Boolean, default=False)
    
    # Auth recovery fields
    verification_otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    income = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    salary_frequency = Column(String, nullable=True)
    
    # JSON or String arrays can be stored depending on DB, but SQLite natively supports JSON in newer versions, or we can use String
    monthly_expenses = Column(String, nullable=True) # Store JSON string
    financial_goals = Column(String, nullable=True) # Store JSON string
    
    risk_level = Column(String, nullable=True)
    investment_experience = Column(String, nullable=True)
    
    emergency_fund = Column(Float, nullable=True)
    existing_investments = Column(Float, nullable=True)
    loan_amount = Column(Float, nullable=True)
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="profile")

import uuid

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    transaction_type = Column(String(50), nullable=False, index=True)  # 'income' or 'expense'
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    merchant = Column(String, nullable=True, index=True)
    payment_method = Column(String, nullable=True)
    description = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    receipt_image = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="transactions")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(String, nullable=True)
    status = Column(String, default="active")
    monthly_target = Column(Float, nullable=True)
    priority = Column(String, default="medium")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="goals")

class ImportSession(Base):
    __tablename__ = "import_sessions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    total_records = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    imported_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    errors = Column(String, default="[]")
    warnings = Column(String, default="[]")
    version = Column(String, default="1.0")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    records = relationship("ImportRecord", back_populates="session", cascade="all, delete-orphan")

class ImportRecord(Base):
    __tablename__ = "import_records"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = Column(String(36), ForeignKey("import_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_data = Column(String, nullable=False)
    parsed_amount = Column(Float, nullable=True)
    parsed_date = Column(String, nullable=True)
    parsed_merchant = Column(String, nullable=True)
    ai_category_suggestion = Column(String, nullable=True)
    is_duplicate = Column(Boolean, default=False)
    status = Column(String, default="STAGED")
    
    session = relationship("ImportSession", back_populates="records")


class ImportAuditLog(Base):
    __tablename__ = "import_audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = Column(String(36), ForeignKey("import_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("ImportSession")

class ReceiptSession(Base):
    __tablename__ = "receipt_sessions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)
    status = Column(String, default="UPLOADED") # UPLOADED, OCR_PROCESSING, COMPLETED, FAILED
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class OCRResult(Base):
    __tablename__ = "ocr_results"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    receipt_session_id = Column(String(36), ForeignKey("receipt_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_text = Column(String, nullable=True)
    confidence_score = Column(Float, default=0.0)
    detected_fields = Column(String, nullable=True) # JSON
    bounding_regions = Column(String, nullable=True) # JSON
    processing_time_ms = Column(Integer, default=0)
    warnings = Column(String, default="[]") # JSON
    errors = Column(String, default="[]") # JSON
    
    session = relationship("ReceiptSession")

class ParsedReceipt(Base):
    __tablename__ = "parsed_receipts"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    receipt_session_id = Column(String(36), ForeignKey("receipt_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_name = Column(String, nullable=True)
    transaction_date = Column(String, nullable=True)
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    warnings = Column(String, default="[]") # JSON
    
    session = relationship("ReceiptSession")

class ReceiptIntelligence(Base):
    __tablename__ = "receipt_intelligence"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    receipt_session_id = Column(String(36), ForeignKey("receipt_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    predicted_category = Column(String, default="Uncategorized")
    field_corrections = Column(String, default="{}") # JSON
    overall_confidence = Column(Float, default=0.0)
    requires_manual_review = Column(Boolean, default=True)
    uncertainty_reasons = Column(String, default="[]") # JSON
    
    session = relationship("ReceiptSession")
