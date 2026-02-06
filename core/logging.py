import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger
from core.context import get_context
from core.config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        ctx = get_context()
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["service"] = "forsee-backend"
        log_record["environment"] = settings.ENVIRONMENT
        
        if ctx:
            if ctx.org_id:
                log_record["org_id"] = str(ctx.org_id)
            if ctx.user_id:
                log_record["user_id"] = str(ctx.user_id)
            # request_id can be added via middleware setting context or contextvar
            if hasattr(ctx, "request_id"):
                log_record["request_id"] = ctx.request_id

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(service)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Silence uvicorn access log to avoid duplicate/non-json logs if desired
    # logging.getLogger("uvicorn.access").disabled = True

logger = logging.getLogger(__name__)
