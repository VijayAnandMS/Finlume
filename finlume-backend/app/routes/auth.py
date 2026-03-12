from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut, Token
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    print("--------------------------------")
    print("--- REGISTRATION TRACE START ---")
    print(f"Incoming username: {repr(user_in.username)}")
    print(f"Incoming password length: {len(user_in.password)}")
    print(f"Engine URL: {str(db.get_bind().url)}")
    print(f"Session ID (hash): {hash(db)}")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_in.username.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    new_user = User(
        username=user_in.username.strip().lower(),
        hashed_password=hash_password(user_in.password)
    )
    db.add(new_user)
    
    print("Executing db.commit()...")
    db.commit()
    print("db.commit() SUCCESS")
    
    print("Executing db.refresh()...")
    db.refresh(new_user)
    print("db.refresh() SUCCESS")
    
    print("--- POST-REGISTRATION DB CHECK ---")
    all_users = db.query(User.username).all()
    print(f"All usernames currently in SAME session DB: {[u[0] for u in all_users]}")
    
    print("Registration Response: 201 Created")
    print("--------------------------------")
    
    return new_user

@router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    print("--------------------------------")
    print(f"Engine URL: {str(db.get_bind().url)}")
    print(f"Username received: {repr(user_in.username)}")
    
    lookup_username = user_in.username.strip().lower()
    user = db.query(User).filter(User.username == lookup_username).first()
    
    print(f"Username found?: {user is not None}")
    
    if not user:
        print("EXACT BRANCH RETURNING 401: if not user:")
        print("--------------------------------")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
        
    is_valid = verify_password(user_in.password, user.hashed_password)
    print(f"verify_password result: {is_valid}")
    
    if not is_valid:
        print("EXACT BRANCH RETURNING 401: if not is_valid:")
        print("--------------------------------")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
        
    print("LOGIN SUCCESS (Returning 200)")
    print("--------------------------------")
    access_token = create_access_token(subject=user.username)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "expiration": settings.JWT_EXPIRE_MINUTES * 60
    }
    


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
