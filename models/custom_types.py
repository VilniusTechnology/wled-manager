from typing import Any, Union
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

def transform_bool_int_str(value: Any) -> bool:
    """Transform various types to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', '1', 'yes', 'on'):
            return True
        if value in ('false', '0', 'no', 'off'):
            return False
        raise ValueError(f'Invalid boolean string value: {value}')
    raise ValueError(f'Expected bool, int, or str, got {type(value)}')

class BoolIntStr:
    """Custom type that accepts boolean, integer, or string values and converts them to boolean."""
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: type[Any] | None,
        _handler: GetJsonSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            function=transform_bool_int_str,
            serialization=core_schema.bool_schema(),
            return_schema=core_schema.bool_schema(),
        )