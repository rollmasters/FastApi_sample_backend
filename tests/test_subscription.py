from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.database import get_db
from app.main import app

from bson import ObjectId
from asgi_lifespan import LifespanManager

from tests.MockDataBase import MockDatabase


@pytest.mark.asyncio
async def test_create_subscription():
    async with LifespanManager(app):  # This will manage the app's lifespan
        # Use httpx AsyncClient for async requests
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Define the request payload
            payload = {
                "email": "test@example.com",
                "date": "2024-10-04T10:20:30"
            }
            # Send POST request to create a subscription
            response = await client.post("/api/v2/person", json=payload)

            # Debugging information to inspect the response
            print(f"Response JSON: {response.json()}")
            print(f"Response Status Code: {response.status_code}")

            # Assert status code is 201 (created)
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"

            # Assert that the correct message is returned
            assert response.json()[
                       "message"] == "Subscription created successfully", f"Message mismatch: {response.json()}"

            # Extract the created person ID from the response
            person_id = response.json()["id"]

            # Cleanup: Delete the created subscription from the database

            database = await get_db()
            await database["Subscriptions"].delete_one({"_id": ObjectId(person_id)})


@pytest.mark.asyncio
async def test_get_people():
    mock_db = MockDatabase(app)
    mock_db.setup()

    # Prepare test data
    test_person = {
        "_id": ObjectId(),
        "email": "test@example.com",
        "date": "2024-10-04T10:20:30"
    }

    # Mock the 'find' method to return the test data
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = [test_person]
    mock_db.add_collection_mock(
        collection_name='Subscriptions',
        method_name='find',
        return_value=mock_cursor
    )

    # Use httpx AsyncClient for async HTTP requests
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send GET request to fetch all people
            response = await client.get("/api/v2/people")

            # Assert status code is 200 (OK)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Assert the response contains the 'people' field
            assert "people" in response.json(), "Response does not contain 'people' field"

            # Assert the response contains the inserted test person
            people = response.json()["people"]
            assert len(people) > 0, "No people found in response"

            # Verify the first person in the list is the one we inserted
            first_person = people[0]
            assert first_person["email"] == test_person["email"], f"Email mismatch: {first_person['email']}"
            assert first_person["date"] == test_person["date"], f"Date mismatch: {first_person['date']}"

    mock_db.teardown()


# Test for database error handling
@pytest.mark.asyncio
async def test_get_people_database_error():
    """Test error handling when there's a database error."""
    mock_db = MockDatabase(app)
    mock_db.setup()

    # Mock the 'find' method to raise an exception
    mock_db.add_collection_mock(
        collection_name='Subscriptions',
        method_name='find',
        side_effect=Exception("Database error")
    )

    # Run the test
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send GET request to fetch all people
            response = await client.get("/api/v2/people")

            # Assert status code is 500 (Internal Server Error)
            assert response.status_code == 500, f"Expected 500, got {response.status_code}"

            # Assert the error message in the response
            expected_detail = "Failed to fetch subscriptions: Database error"
            assert response.json()[
                       "detail"] == expected_detail, f"Expected detail '{expected_detail}', got '{response.json()['detail']}'"

    mock_db.teardown()


# Test for empty collection
@pytest.mark.asyncio
async def test_get_people_empty_collection():
    """Test the case where there are no people in the collection."""
    mock_db = MockDatabase(app)
    mock_db.setup()

    # Mock the 'find' method to return an empty async iterator
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = []
    mock_db.add_collection_mock(
        collection_name='Subscriptions',
        method_name='find',
        return_value=mock_cursor
    )

    # Run the test
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send GET request to fetch all people
            response = await client.get("/api/v2/people")

            # Assert status code is 200 (OK)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Assert the response contains the 'people' field and it is empty
            assert "people" in response.json(), "Response does not contain 'people' field"
            assert len(response.json()["people"]) == 0, "Expected no people, but found some in the response"

    mock_db.teardown()
