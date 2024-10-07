import pytest
from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient

from app.main import app
from tests.MockDataBase import MockDatabase

# Fixture to handle FastAPI app lifespan, allowing start-up and shutdown events to be tested
@pytest.fixture(scope="function")  # Changed to function scope to prevent issues with async context
async def app_lifespan():
    async with LifespanManager(app):
        yield

# Fixture to create an async client for tests
@pytest.fixture
def test_client():
    return TestClient(app)
# Fixture to use MockDatabase to override the get_db dependency
@pytest.fixture
def mock_db(app_lifespan):  # Ensure app_lifespan is included to make sure the app is available
    mock_db_instance = MockDatabase(app)
    mock_db_instance.setup()  # Override get_db dependency with mock
    yield mock_db_instance
    mock_db_instance.teardown()  # Clean up after tests
