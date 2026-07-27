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
