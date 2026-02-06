from typing import Dict, Any, Optional
import httpx
from core.config import settings
from fastapi import HTTPException, status

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

async def get_google_auth_url() -> str:
    """
    Generates the Google OAuth2 Authorization URL.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Google OAuth not configured"
        )
    
    # Scope: openid email profile
    scope = "openid email profile"
    
    return (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"include_granted_scopes=true"
    )

async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """
    Exchanges the authorization code for an access token.
    """
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to exchange code: {response.text}"
        )
        
    return response.json()

async def get_google_user_info(token: str) -> Dict[str, Any]:
    """
    Fetches user information using the access token.
    Checks ID token would be better, but user info endpoint is requested.
    """
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(user_info_url, headers=headers)
        
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch user info"
        )
        
    return response.json()
