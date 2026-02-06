from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app
from models.user import User

client = TestClient(app)

@pytest.fixture
def mock_google_auth():
    with patch("services.google_auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange, \
         patch("services.google_auth.get_google_user_info", new_callable=AsyncMock) as mock_info:
        yield mock_exchange, mock_info

def test_google_login_url():
    """Test getting the auth URL."""
    # Ensure settings are mocked or set in env. 
    # For this test, valid settings are needed in config or mocked.
    # Assuming config reads from env which might be empty during test if not set.
    # We can patch settings.
    with patch("core.config.settings.GOOGLE_CLIENT_ID", "test_id"), \
         patch("core.config.settings.GOOGLE_REDIRECT_URI", "test_uri"):
        response = client.post("/api/v1/auth/google/login")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "client_id=test_id" in data["auth_url"]

def test_google_callback_new_user(mock_google_auth, db_session): 
    # db_session fixture likely needs to be defined if we rely on DB. 
    # BUT, TestClient uses the app. If the app uses `deps.get_db`, we might need to override valid DB.
    # For now, let's assume the environment connects to a test DB or mock the DB dependency.
    # Given the complexity, I'll rely on the fact that existing tests (if any) handle DB.
    # If no existing tests, I'll attempt to verify response structure primarily.
    
    mock_exchange, mock_info = mock_google_auth
    
    mock_exchange.return_value = {"access_token": "fake_token"}
    mock_info.return_value = {
        "email": "newuser@example.com",
        "name": "New Google User",
        "id": "google_123"
    }
    
    # We need to ensure the user doesn't exist.
    # This might be tricky without a clean DB state.
    # Let's clean up after ourselves if possible or use a unique email.
    email = f"google_test_{pytest.importorskip('uuid').uuid4()}@example.com"
    mock_info.return_value["email"] = email
    
    response = client.get("/api/v1/auth/google/callback?code=valid_code")
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "VIEWER"
    assert data["user"]["org_id"] is not None

def test_google_callback_existing_user(mock_google_auth):
    mock_exchange, mock_info = mock_google_auth
    
    mock_exchange.return_value = {"access_token": "fake_token_2"}
    email = f"existing_{pytest.importorskip('uuid').uuid4()}@example.com"
    
    mock_info.return_value = {
        "email": email,
        "name": "Existing User",
        "id": "google_456"
    }
    
    # First call creates the user
    response1 = client.get("/api/v1/auth/google/callback?code=code1")
    assert response1.status_code == 200
    user_id = response1.json()["user"]["id"]
    
    # Second call logs in
    response2 = client.get("/api/v1/auth/google/callback?code=code2")
    assert response2.status_code == 200
    assert response2.json()["user"]["id"] == user_id
