import pytest
from tests.MockDataBase import MockDatabase, MockInsertOneResult
from fastapi.testclient import TestClient
sample_data = {
    "firstName": "John",
    "email": "john.doe@example.com",
    "website": "https://example.com",
    "goals": "Understand your product features."
}

# Mocking the email sending function
def mock_send_email(recipients, subject, body):
    pass


@pytest.fixture
def mock_email(monkeypatch):
    # Mock the send_email function
    monkeypatch.setattr(
        'app.api.v2.endpoints.betasignup.send_email',
        mock_send_email
    )
@pytest.mark.asyncio
async def test_demo_endpoint_success(test_client:TestClient, mock_db:MockDatabase, mock_email):
    mock_insert_one_result = MockInsertOneResult(inserted_id="mock_id")

    mock_db.add_collection_mock(
        collection_name="demo",
        method_name="insert_one",
        return_value=mock_insert_one_result
    )
    response = test_client.post("/api/v2/demo", json=sample_data)
    assert response.status_code == 201
    assert response.json()["firstName"] == sample_data["firstName"]
    assert response.json()["email"] == sample_data["email"]
    assert response.json()["website"] == sample_data["website"]
    assert response.json()["goals"] == sample_data["goals"]

@pytest.mark.asyncio
async def test_demo_endpoint_validation_error(test_client):
    # Missing required field 'email'
    invalid_data = sample_data.copy()
    del invalid_data['email']

    response = test_client.post("/api/v2/demo", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()['detail'][0]['loc'] == ['body', 'email']
    assert response.json()['detail'][0]['msg'] == 'field required'
@pytest.mark.asyncio
async def test_demo_endpoint_invalid_email(test_client):
    # Invalid email format
    invalid_data = sample_data.copy()
    invalid_data['email'] = 'not-an-email'

    response = test_client.post("/api/v2/demo", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity
    assert response.json()['detail'][0]['loc'] == ['body', 'email']
    assert response.json()['detail'][0]['msg'] == 'value is not a valid email address'