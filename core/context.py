import contextvars
from typing import Optional
from models.user import Role
from uuid import UUID

class RequestContext:
    def __init__(self, user_id: Optional[UUID] = None, org_id: Optional[UUID] = None, role: Optional[Role] = None, api_key_id: Optional[UUID] = None, request_id: Optional[str] = None):
        self.user_id = user_id
        self.org_id = org_id
        self.role = role
        self.api_key_id = api_key_id
        self.request_id = request_id

_request_context = contextvars.ContextVar("request_context", default=None)

def get_context() -> Optional[RequestContext]:
    return _request_context.get()

def set_context(context: RequestContext):
    _request_context.set(context)
