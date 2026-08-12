import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter
from app.core.config import settings
from app.core.logging_config import log_audit_action
from app.routes import (
    auth, profile, transactions, summary, chat, advisor, 
    goals, goal_planner, investment, monitoring,
    demo, export, intelligence, imports, receipts
)

from contextlib import asynccontextmanager
import uuid
import logging
from app.core.logging_config import request_id_ctx_var
from fastapi.responses import JSONResponse

main_logger = logging.getLogger(__name__)

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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = request_id_ctx_var.get()
    main_logger.error(f"Unhandled Server Error: {exc}", extra={"request_id": req_id})
    # Safe tracing returning sanitized output statically securely organically cleanly
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "error_reference": req_id}
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    req_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request_id_ctx_var.set(req_id)
    
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        # Re-raise to let exception handler catch it
        raise e
    finally:
        process_time = time.time() - start_time
        
        # Log purely analytics dynamically 
        log_audit_action(
            "system", 
            f"API {request.method} {request.url.path}", 
            "Success" if 'response' in locals() and response.status_code < 400 else "Error", 
            process_time * 1000
        )
        
    if 'response' in locals():
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Correlation-ID"] = req_id
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
app.include_router(imports.router)
app.include_router(receipts.router)
