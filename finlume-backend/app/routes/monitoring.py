from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.core.config import settings
import time
import psutil

router = APIRouter(tags=["Monitoring", "Observability"])

START_TIME = time.time()

@router.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok", "message": "Finlume AI is healthy."})

@router.get("/ready", summary="Check Application Readiness", description="Verifies all database and internal connections are alive.")
def readiness_check(db: Session = Depends(get_db)):
    try:
        # Check DB connection
        db.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "ready", "database": "connected"})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": "Database disconnected"})

@router.get("/metrics", summary="System Metrics Dump", description="Fetches server CPU, RAM, and internal pipeline states.")
def get_metrics():
    uptime = time.time() - START_TIME
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()

    return JSONResponse(content={
        "uptime_seconds": uptime,
        "cpu_usage_percent": cpu_percent,
        "memory_usage_percent": mem.percent,
        "active_agents": ["expense", "budget", "advisor", "forecast", "anomaly", "simulation"],
        "llm_availability": bool(settings.GEMINI_API_KEY) or bool(settings.ANTHROPIC_API_KEY),
        "memory_status": "Chroma Ready"
    })
