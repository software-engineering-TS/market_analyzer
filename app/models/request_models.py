"""Validated API request models."""

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    user_name: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Unique username",
    )
    email_id: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Password (maximum 72 UTF-8 bytes for bcrypt compatibility)",
    )

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes.")
        return value


class LoginRequest(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=64)

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes.")
        return value
