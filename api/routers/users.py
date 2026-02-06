from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api import deps
from models.user import User, Role
from schemas.user import User as UserSchema, UserCreate

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.require_admin), # Only admins can list users
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(User).filter(User.org_id == current_user.org_id).offset(skip).limit(limit).all()
    return users

@router.post("/invite", response_model=UserSchema)
def invite_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.require_admin),
) -> Any:
    """
    Invite new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    # Enforce Org ID from current user
    user_obj = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password), # In real app, generate temp password/link
        full_name=user_in.full_name,
        role=user_in.role,
        org_id=current_user.org_id, # Must belong to same org
        is_active=True
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
