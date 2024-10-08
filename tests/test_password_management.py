from unittest.mock import MagicMock

import pytest
from bson import ObjectId
from fastapi import status
from app.main import app

from app.core.config import settings
from tests.test_auth import mock_decode_access_token


def mock_create_access_token(data: dict, expires_delta=None):
    return "mock_reset_token"


# Mock the send_email function
def mock_send_email(to_email: str, subject: str, body: str):
    # You can add assertions here if needed
    pass


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Patch create_access_token in the module where it's used
    monkeypatch.setattr(
        'app.api.v2.endpoints.auth.create_access_token',
        mock_create_access_token
    )
    # Patch send_email in the module where it's used
    monkeypatch.setattr(
        'app.api.v2.endpoints.auth.send_email',
        mock_send_email)
    monkeypatch.setattr('app.api.v2.endpoints.auth.decode_access_token', mock_decode_access_token)
    # Patch get_password_hash in the module where it's used
    monkeypatch.setattr('app.api.v2.endpoints.auth.get_password_hash', mock_get_password_hash)


def test_forgot_password_success(test_client, mock_db):
    # Mock user data
    user_id = ObjectId("60d21b4667d0d8992e610c85")
    user_data = {
        "_id": user_id,
        "email": "johndoe@example.com",
        "hashed_password": "hashedpassword123",
        "is_active": True,
        "is_verified": True,
        "full_name": "John Doe"
    }

    # Mock the database find_one method to return user_data
    mock_db.add_collection_mock(
        "Registered_users",
        "find_one",
        return_value=user_data
    )

    # Prepare the request data
    email = "johndoe@example.com"

    # Send POST request to /forgot-password
    response = test_client.post("api/v2/forgot-password", json={"email": email})

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password reset email sent"}


def test_forgot_password_email_not_found(test_client, mock_db):
    # Mock the database find_one method to return None
    mock_db.add_collection_mock(
        "Registered_users",
        "find_one",
        return_value=None
    )

    # Prepare the request data
    email = "nonexistent@example.com"

    # Send POST request to /forgot-password
    response = test_client.post("api/v2/forgot-password", json={"email": email})

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Email not found"}


def mock_get_password_hash(password: str):
    return "hashed_" + password  # Simple mock hash for testing




def test_reset_password_success(test_client, mock_db):
    # Mock the database update_one method to simulate successful update
    mock_db.add_collection_mock(
        "Registered_users",
        "update_one",
        return_value=MagicMock(modified_count=1)
    )

    # Prepare the request parameters
    params = {
        "token": "valid_token",
        "new_password": "new_secure_password"
    }

    # Send GET request to /reset-password
    response = test_client.post("api/v2/reset-password", json=params)

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password reset successful"}


def test_reset_password_invalid_token(test_client):
    # Prepare the request parameters
    params = {
        "token": "invalid_token",
        "new_password": "new_secure_password"
    }

    # Send GET request to /reset-password
    response = test_client.post("api/v2/reset-password", json=params)

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid or expired token"}


def test_reset_password_token_without_user_id(test_client):
    # Prepare the request parameters
    params = {
        "token": "token_without_user_id",
        "new_password": "new_secure_password"
    }

    # Send GET request to /reset-password
    response = test_client.post("api/v2/reset-password", json=params)

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid or expired token"}


def test_reset_password_user_not_found(test_client, mock_db):
    # Mock the database update_one method to simulate no document updated
    mock_db.add_collection_mock(
        "Registered_users",
        "update_one",
        return_value=MagicMock(modified_count=0)
    )

    # Prepare the request parameters
    params = {
        "token": "valid_token",
        "new_password": "new_secure_password"
    }

    # Send GET request to /reset-password
    response = test_client.post("api/v2/reset-password", json=params)

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "User not found"}
