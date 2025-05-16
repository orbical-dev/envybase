from pydantic import BaseModel, EmailStr, Field
from config import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
)


class LoginData(BaseModel):
    """
    Data model for user login.
    """

    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description=f"Must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters",
    )


class RegisterData(BaseModel):
    """
    Data model for user registration.
    """

    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        description=f"Must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters",
    )
    name: str = Field(..., description="Name of the user")
    username: str = Field(
        ...,
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        description=f"Username of the user, must be {USERNAME_MIN_LENGTH}-{USERNAME_MAX_LENGTH} characters",
    )

