from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    phone_number: Optional[str] = None

class UserOut(BaseModel):
    id: int
    full_name: Optional[str] = None
    username: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_email_verified: bool
    profile_completed: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VerifyEmailRequest(BaseModel):
    email: str
    otp: str

class ResendOTPRequest(BaseModel):
    email: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserProfileData(BaseModel):
    income: Optional[float] = None
    currency: Optional[str] = "USD"
    salary_frequency: Optional[str] = None
    monthly_expenses: Optional[str] = None
    financial_goals: Optional[str] = None
    risk_level: Optional[str] = None
    investment_experience: Optional[str] = None
    emergency_fund: Optional[float] = None
    existing_investments: Optional[float] = None
    loan_amount: Optional[float] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expiration: int

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    transaction_date: str  # YYYY-MM-DD
    transaction_type: str  # 'income' or 'expense'
    category: str
    subcategory: Optional[str] = None
    amount: float
    currency: Optional[str] = "USD"
    merchant: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    receipt_image: Optional[str] = None

class TransactionOut(BaseModel):
    id: str
    user_id: int
    transaction_date: str
    transaction_type: str
    category: str
    subcategory: Optional[str]
    amount: float
    currency: str
    merchant: Optional[str]
    payment_method: Optional[str]
    description: Optional[str]
    notes: Optional[str]
    tags: Optional[str]
    receipt_image: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Goal Schemas ---
class GoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[str] = None
    status: str = "active"
    monthly_target: Optional[float] = None
    priority: str = "medium"

class GoalOut(BaseModel):
    id: int
    user_id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[str]
    status: str
    monthly_target: Optional[float]
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Summary Schemas ---
class CategorySummary(BaseModel):
    category: str
    amount: float

class SummaryOut(BaseModel):
    total_income: float
    total_expense: float
    net: float
    top_categories: List[CategorySummary]
    transactions: List[TransactionOut]

# --- Chat Schemas ---
class ChatMessage(BaseModel):
    message: str

class ChatReply(BaseModel):
    reply: str
    agents_used: List[str] = []
