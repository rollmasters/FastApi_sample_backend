from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from typing import Any, Optional
from app.database import get_db  # Adjust the import to match where get_db is defined

class MockInsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class MockDatabase:
    def __init__(self, app: FastAPI):
        self.app = app
        self.mock_db_instance = MagicMock()  # Use MagicMock for collections
        self.original_dependency_overrides = app.dependency_overrides.copy()

    def add_collection_mock(
        self,
        collection_name: str,
        method_name: str,
        *,
        side_effect: Optional[Exception] = None,
        return_value: Optional[Any] = None
    ) -> AsyncMock:
        # Ensure the collection mock exists
        if collection_name not in self.mock_db_instance:
            self.mock_db_instance[collection_name] = MagicMock()

        collection_mock = self.mock_db_instance[collection_name]

        # Create an AsyncMock for the method (since DB methods like find_one are async)
        method_mock = AsyncMock()
        setattr(collection_mock, method_name, method_mock)
        method_mock.side_effect = side_effect
        method_mock.return_value = return_value
        # Set the side effect or return value
        # if side_effect is not None:
        #     method_mock.side_effect = side_effect
        # elif return_value is not None:
        #     method_mock.return_value = return_value
        # else:
        #     method_mock.return_value = AsyncMock()  # Default to an AsyncMock return value

        return method_mock

    async def _mock_get_db(self):
        yield self.mock_db_instance

    async def _get_db_spatial_ai(self):
        yield self.mock_db_instance

    def setup(self):
        """
        Override the get_db dependency with the mock database.
        """
        self.app.dependency_overrides[get_db] = self._mock_get_db

    def teardown(self):
        """
        Remove the dependency override to clean up after tests.
        """
        self.app.dependency_overrides = self.original_dependency_overrides.copy()
