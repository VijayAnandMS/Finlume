import random
import datetime
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.models.models import User
from app.schemas.schemas import (
    UserCreate, UserOut, Token, 
    VerifyEmailRequest, ResendOTPRequest, 
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    # Extract identity
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Optional logic: could block here if not verified, but block at login is standard.
    return user

@router.post("/register", response_model=UserOut, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check uniqueness
    lookup_user = user_in.username.strip().lower()
    lookup_email = user_in.email.strip().lower()

    if db.query(User).filter(User.username == lookup_user).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == lookup_email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    otp = str(random.randint(100000, 999999))
    expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    
    print(f"\n========== OTP DELIVERY ==========\nTO: {lookup_email}\nCODE: {otp}\nExpires in 15 minutes.\n==================================")
    
    new_user = User(
        full_name=user_in.full_name,
        username=lookup_user,
        email=lookup_email,
        phone_number=user_in.phone_number,
        hashed_password=hash_password(user_in.password),
        verification_otp=otp,
        otp_expiry=expiry
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.is_email_verified:
        return {"status": "success", "message": "Email already verified"}
        
    if not user.verification_otp or user.verification_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if user.otp_expiry and user.otp_expiry.replace(tzinfo=datetime.timezone.utc) < datetime.datetime.now(datetime.timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")
        
    user.is_email_verified = True
    user.verification_otp = None
    user.otp_expiry = None
    db.commit()
    return {"status": "success", "message": "Email verified successfully"}

@router.post("/resend-otp")
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_email_verified:
        return {"status": "success", "message": "User already verified."}
        
    otp = str(random.randint(100000, 999999))
    user.verification_otp = otp
    user.otp_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    
    db.commit()
    print(f"\n========== NEW OTP DELIVERY ==========\nTO: {user.email}\nCODE: {otp}\n======================================")
    
    return {"status": "success", "message": "OTP sent"}

# Handle BOTH custom json payload and OAuth2 form data
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form_data.username can actually contain email or username in this workflow
    identity = form_data.username.strip().lower()
    
    user = db.query(User).filter(
        or_(User.username == identity, User.email == identity)
    ).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before signing in.")
        
    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    
    access_token = create_access_token(subject=user.username)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expiration": settings.JWT_EXPIRE_MINUTES * 60,
        "profile_completed": user.profile_completed
    }

@router.post("/custom-login")
def custom_login(payload: dict, db: Session = Depends(get_db)):
    # Frontend fallback hook for direct payload processing instead of OAuth form
    identity = payload.get("identity", "").strip().lower()
    password = payload.get("password", "")
    
    user = db.query(User).filter(
        or_(User.username == identity, User.email == identity)
    ).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before signing in.")
        
    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    
    access_token = create_access_token(subject=user.username)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expiration": settings.JWT_EXPIRE_MINUTES * 60,
        "profile_completed": user.profile_completed
    }

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if user:
        token = str(uuid.uuid4())
        user.reset_token = token
        user.reset_token_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        db.commit()
        print(f"\n========== PASSWORD RESET ==========\nTO: {user.email}\nTOKEN: {token}\n======================================")
        
    return {"status": "success", "message": "If an account exists, a reset instruction has been logged."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == req.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    if user.reset_token_expiry and user.reset_token_expiry.replace(tzinfo=datetime.timezone.utc) < datetime.datetime.now(datetime.timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")
        
    user.hashed_password = hash_password(req.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    
    return {"status": "success", "message": "Password updated successfully."}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
