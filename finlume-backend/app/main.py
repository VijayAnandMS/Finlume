import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logging_config import log_audit_action
from app.routes import (
    auth, profile, transactions, summary, chat, advisor, 
    goals, goal_planner, investment, monitoring,
    demo, export, intelligence
)

from contextlib import asynccontextmanager

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"INFO: Database engine active: {settings.DATABASE_URL}")
    yield

app = FastAPI(
    title="Finlume Backend",
    description="FastAPI Backend for Finlume AI",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Simple Audit Log mapping for analytics requests
    if "/api/agents" in request.url.path:
        log_audit_action("system", f"Called endpoint: {request.url.path}", "Success", process_time * 1000)
        
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# CORS configuration
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",  # Explicit fallback for dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(transactions.router)
app.include_router(summary.router)
app.include_router(chat.router)
app.include_router(advisor.router)
app.include_router(goals.router)
app.include_router(goal_planner.router)
app.include_router(investment.router)
app.include_router(monitoring.router)
app.include_router(demo.router)
app.include_router(export.router)
app.include_router(intelligence.router)
