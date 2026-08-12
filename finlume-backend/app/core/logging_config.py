import logging
from pythonjsonlogger import jsonlogger
import sys
import time
import contextvars
import uuid

# Define global context var for correlation tracing
request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")

class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get()
        return True

def setup_audit_logging():
    import os
    from logging.handlers import TimedRotatingFileHandler
    
    logger = logging.getLogger("finlume_audit")
    logger.setLevel(logging.INFO)
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    if not logger.handlers:
        # File handler wrapping rotation at midnight
        fileHandler = TimedRotatingFileHandler("logs/finlume_audit.log", when="midnight", interval=1, backupCount=30)
        
        # Dual handler pushing to file and stdout sequentially
        logHandler = logging.StreamHandler(sys.stdout)
        
        formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(request_id)s %(user_id)s %(action)s %(status)s %(execution_time_ms)s')
        fileHandler.setFormatter(formatter)
        logHandler.setFormatter(formatter)
        
        # Add correlation ID filter
        fileHandler.addFilter(CorrelationIdFilter())
        logHandler.addFilter(CorrelationIdFilter())
        
        logger.addHandler(fileHandler)
        logger.addHandler(logHandler)

        
    return logger

audit_logger = setup_audit_logging()

def log_audit_action(user_id: str, action: str, status: str, exec_time_ms: float = 0.0):
    audit_logger.info("Audit Entry", extra={
        "timestamp": time.time(),
        "user_id": user_id,
        "action": action,
        "status": status,
        "execution_time_ms": exec_time_ms
    })
