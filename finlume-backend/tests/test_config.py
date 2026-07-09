from app.core.config import settings

def test_settings_loaded():
    assert settings.DATABASE_URL is not None
    assert settings.DATABASE_URL != ""
    
    assert settings.JWT_SECRET is not None
    assert settings.JWT_SECRET != ""
    
    assert settings.JWT_ALGORITHM == "HS256"
    
    assert settings.GEMINI_MODEL is not None
    assert settings.GEMINI_MODEL != ""
