from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api import deps
from core import security, config
from models.user import User, Organization, Role
from schemas.user import Token, UserCreate, User as UserSchema
from services import google_auth
import uuid

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, user.org_id, user.role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    
    # Auto-create organization if not invited (simplified for now)
    # If org_id is not provided, we create a new Organization
    if not user_in.org_id:
        org = Organization(name=f"{user_in.full_name}'s Org")
        db.add(org)
        db.flush() # to get ID
        user_in.org_id = org.id
        user_in.role = Role.ADMIN # Creator is Admin
    
    user_obj = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        org_id=user_in.org_id,
        is_active=True
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.post("/google/login")
async def google_login():
    """
    Returns the Google OAuth2 authorization URL.
    The frontend should redirect the user to this URL.
    """
    auth_url = await google_auth.get_google_auth_url()
    return {"auth_url": auth_url}

@router.get("/google/callback", response_model=Token)
async def google_callback(code: str, db: Session = Depends(deps.get_db)):
    """
    Exchanges authorization code for access token and logs in/creates user.
    """
    # 1. Exchange code
    token_res = await google_auth.exchange_code_for_token(code)
    access_token = token_res.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token from Google")
        
    # 2. Get User Info
    user_info = await google_auth.get_google_user_info(access_token)
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google user info does not contain email")
        
    # 3. Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Create new user
        # Assign to new personal org (following register pattern)
        # Or check domain? Prompt: "Assign to organization based on email domain OR default org"
        # I'll implement 'New Personal Org' as default behavior to match local registration
        
        org = Organization(name=f"{user_info.get('name', 'User')}'s Org")
        db.add(org)
        db.flush()
        
        user = User(
            email=email,
            hashed_password=security.get_password_hash(str(uuid.uuid4())), # Random password
            full_name=user_info.get("name"),
            role=Role.VIEWER, # Default role
            org_id=org.id,
            is_active=True,
            oauth_provider="google",
            oauth_provider_id=user_info.get("id")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update oauth info if missing?
        if user.oauth_provider != "google":
            # Optional: Link account. For now, just logging in is fine.
            pass
            
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 4. Issue JWT
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, user.org_id, user.role, expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "org_id": str(user.org_id)
        }
    }
