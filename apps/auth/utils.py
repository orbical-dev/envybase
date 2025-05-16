import bcrypt
from typing import Dict
from datetime import datetime, timezone
import jwt
from config import ISSUER, AUTH_KEY
import string
import secrets

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_jwt_token(data: Dict) -> str:
    """Creates a JWT token"""
    to_encode = data.copy()
    to_encode.update({"iat": datetime.now(timezone.utc), "iss": ISSUER})

    return jwt.encode(to_encode, AUTH_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> Dict:
    """
    Decodes and validates a JWT token.

    Args:
        token: The JWT token string to decode.

    Returns:
        The decoded payload as a dictionary.

    Raises:
        ValueError: If the token is expired or invalid.
    """
    try:
        payload = jwt.decode(token, AUTH_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError(
            "Token has expired"
        )  # This shouldn't happen, the JWT creator doesn't set an expiration time
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def generate_username():
    """
    Generates a random 12-character username using ASCII letters and digits.

    Returns:
        A securely generated username consisting of uppercase, lowercase letters, and digits.
    """
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(12))
