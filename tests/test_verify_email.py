import pytest
from fastapi import status
from unittest.mock import MagicMock
from bson import ObjectId
from app.main import app


# Mock the decode_access_token function
def mock_decode_access_token(token: str):
    if token == "valid_token":
        return {"user_id": "60d21b4667d0d8992e610c85"}
    elif token == "invalid_token":
        return None
    elif token == "token_without_user_id":
        return {
            "test": "test"
        }
    else:
        return None


# Patch the decode_access_token function using the monkeypatch fixture
@pytest.fixture(autouse=True)
def patch_decode_access_token(monkeypatch):
    monkeypatch.setattr(
        'app.api.v2.endpoints.auth.decode_access_token',
        mock_decode_access_token
    )


def test_verify_email_success(test_client, mock_db):
    # Mock the database update_one method to simulate successful update
    mock_db.add_collection_mock(
        "Users",
        "update_one",
        return_value=MagicMock(modified_count=1)
    )

    # Prepare the request data
    token_data = {
        "token": "valid_token"
    }

    # Send POST request to /verify-email
    response = test_client.post("api/v2/verify-email", json=token_data)

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "User verified successfully"}


def test_verify_email_invalid_token(test_client):
    # Prepare the request data
    token_data = {
        "token": "invalid_token"
    }

    # Send POST request to /verify-email
    response = test_client.post("api/v2/verify-email", json=token_data)

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid or expired token"}


def test_verify_email_token_without_user_id(test_client):
    # Prepare the request data
    token_data = {
        "token": "token_without_user_id"
    }

    # Send POST request to /verify-email
    response = test_client.post("api/v2/verify-email", json=token_data)

    # Assert response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid token"}


def test_verify_email_user_not_found_or_already_verified(test_client, mock_db):
    # Mock the database update_one method to simulate no document updated
    mock_db.add_collection_mock(
        "Users",
        "update_one",
        return_value=MagicMock(modified_count=0)
    )

    # Prepare the request data
    token_data = {
        "token": "valid_token"
    }

    # Send POST request to /verify-email
    response = test_client.post("api/v2/verify-email", json=token_data)

    # Assert response
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found or already verified"}
