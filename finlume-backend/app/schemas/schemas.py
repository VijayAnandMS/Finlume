from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    expiration: int

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    date: str  # YYYY-MM-DD
    category: str
    type: str  # 'income' or 'expense'
    amount: float
    description: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    user_id: int
    date: str
    category: str
    type: str
    amount: float
    description: Optional[str]
    created_at: datetime

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
