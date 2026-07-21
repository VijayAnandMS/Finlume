import sys
import os

# Add backend directory to sys path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

def ensure_test_user():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "testuser123").first()
    if not user:
        user = User(
            full_name="E2E Test User",
            username="testuser123",
            email="test@finlume.ai",
            hashed_password=get_password_hash("Password123!"),
            is_verified=True,
            profile_completed=False,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Created testuser123 successfully.")
    else:
        # Reset profile completed to test onboarding
        user.profile_completed = False
        user.hashed_password = get_password_hash("Password123!")
        db.commit()
        print("testuser123 already exists. Reset profile_completed.")
    db.close()

if __name__ == "__main__":
    ensure_test_user()
