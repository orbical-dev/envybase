from pydantic import BaseModel, EmailStr, Field
from config import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


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
