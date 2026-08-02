from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=50,
    )

    last_name: str = Field(
        min_length=2,
        max_length=50,
    )

    phone_number: str = Field(
        min_length=10,
        max_length=20,
    )