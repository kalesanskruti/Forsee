from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from models.user import Role

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Role = Role.VIEWER

class UserCreate(UserBase):
    password: str
    org_id: Optional[UUID] = None # Or invite flow

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: UUID
    org_id: UUID
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None # user_id
    org_id: Optional[str] = None
    role: Optional[str] = None
