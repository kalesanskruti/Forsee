from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Global Limiter
# In production, use Redis storage backend
limiter = Limiter(key_func=get_remote_address)
