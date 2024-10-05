from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema, CoreSchema
from pydantic.json_schema import JsonSchemaValue

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # Define the core schema for validation
        return core_schema.general_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetCoreSchemaHandler
    ) -> JsonSchemaValue:
        # Generate JSON schema representation for the PyObjectId
        json_schema = handler(core_schema)
        json_schema.update(type="string", example="60d21b4667d0d8992e610c85")
        return json_schema

    @classmethod
    def validate(cls, v, field):
        """Validate that the input is a valid ObjectId"""
        if isinstance(v, ObjectId):
            return str(v)  # Convert ObjectId to string for validation
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(ObjectId(v))  # Convert valid ObjectId string back to string

