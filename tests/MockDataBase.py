# test_utils.py

from unittest.mock import AsyncMock
from fastapi import FastAPI
from typing import Any, Optional
from app.database import get_db  # Adjust the import to match where get_db is defined


class MockDatabase:
    def __init__(self, app: FastAPI):
        self.app = app
        self.mock_db_instance = AsyncMock()
        self.original_dependency_overrides = app.dependency_overrides.copy()

    def add_collection_mock(
        self,
        collection_name: str,
        method_name: str,
        *,
        side_effect: Optional[Exception] = None,
        return_value: Optional[Any] = None
    ) -> AsyncMock:
        """
        Mock a method on a collection in the database.

        :param collection_name: Name of the collection to mock.
        :param method_name: Name of the method to mock (e.g., 'find', 'insert_one').
        :param side_effect: An exception to raise when the method is called.
        :param return_value: The value to return when the method is called.
        :return: The mocked method.
        """
        collection_mock = self.mock_db_instance[collection_name]
        method_mock = getattr(collection_mock, method_name)
        if side_effect is not None:
            method_mock.side_effect = side_effect
        elif return_value is not None:
            method_mock.return_value = return_value
        else:
            method_mock.return_value = AsyncMock()
        return method_mock

    async def _mock_get_db(self):
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
