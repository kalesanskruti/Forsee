import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import Request as FastAPIRequest
from core import context
from core.logging import logger
import traceback

class OperationalMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Init base context with request_id
        ctx = context.RequestContext(request_id=request_id)
        context.set_context(ctx)
        
        response = None
        try:
            response = await call_next(request)
            
            # Add trace id to header
            response.headers["X-Request-ID"] = request_id
            
            # Log successful request (or managed error)
            duration = time.time() - start_time
            logger.info(
                f"Request finished",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration": duration,
                    "ip": request.client.host
                }
            )
            
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(exc)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration": duration,
                    "stack_trace": traceback.format_exc()
                }
            )
            
            # Global Exception Handler formatting
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal error occurred. Please contact support.",
                    "trace_id": request_id
                }
            )
            
        return response
