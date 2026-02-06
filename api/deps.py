from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from core import config, security, context
from db.session import SessionLocal
from models.user import User, Role, ApiKey
from schemas.user import TokenPayload
from uuid import UUID

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{config.settings.API_V1_STR}/auth/login")
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Set Requests Context
    # We maintain the request_id init in middleware
    existing_ctx = context.get_context()
    request_id = existing_ctx.request_id if existing_ctx else None

    ctx = context.RequestContext(
        user_id=user.id,
        org_id=user.org_id,
        role=user.role,
        request_id=request_id
    )
    context.set_context(ctx)
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[ApiKey]:
    if not api_key:
        return None
    
    # In real app, hash the key and check. 
    # For this simplified version (and since we store hashed or prefix), we assume check logic.
    # Assuming the header sends the raw key.
    # We'll just look it up.
    
    # IMPORTANT: In a real implementation we would look up by hash.
    # For now, let's assume we can match it.
    
    key_obj = db.query(ApiKey).filter(ApiKey.key_hash == security.get_key_hash(api_key)).first()
    if key_obj:
        existing_ctx = context.get_context()
        request_id = existing_ctx.request_id if existing_ctx else None
        
        ctx = context.RequestContext(
            user_id=key_obj.user_id,
            org_id=key_obj.org_id,
            api_key_id=key_obj.id,
            role=Role.ENGINEER, # API Keys typically imply engineer/system access
            request_id=request_id
        )
        context.set_context(ctx)
        return key_obj
    raise HTTPException(status_code=403, detail="Invalid API Key")

def require_role(allowed_roles: List[Role]):
    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

