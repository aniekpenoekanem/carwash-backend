from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    """Base schema for all API models."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )