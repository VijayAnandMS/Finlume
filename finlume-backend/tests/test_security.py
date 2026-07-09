from datetime import timedelta
from app.core.security import hash_password, verify_password, create_access_token, verify_token

def test_password_hashing():
    password = "my_secure_password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_flow():
    subject = "12345"
    token = create_access_token(subject)
    assert token
    
    decoded = verify_token(token)
    assert decoded == subject

def test_invalid_or_expired_jwt():
    # Expired token
    expired_token = create_access_token("12345", expires_delta=timedelta(seconds=-10))
    assert verify_token(expired_token) is None
    
    # Tampered token
    valid_token = create_access_token("12345")
    tampered_token = valid_token + "invalid_suffix"
    assert verify_token(tampered_token) is None
