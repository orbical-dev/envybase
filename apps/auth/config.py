import os
from dotenv import load_dotenv

load_dotenv()

# ANSI color constants
ERROR_COLOR = "\033[31m[ERROR]\033[0m \033[107m"
COLOR_RESET = "\033[0m"


def format_error_message(message: str) -> str:
    return f"{ERROR_COLOR}{message}{COLOR_RESET}"


if not os.getenv("MONGO_URI"):
    raise ValueError(
        format_error_message("MONGO_URI not set, please set it in the .env file"),
    )

if not os.getenv("REDIS_HOST"):
    raise ValueError(
        format_error_message("REDIS_HOST not set, please set it in the .env file"),
    )

if not os.getenv("REDIS_PORT"):
    print("\033[33m[WARN]\033[0m REDIS_PORT not set, using default value of 6379")

MONGO_URI = os.getenv("MONGO_URI")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

if not os.getenv("PASSWORD_MIN_LENGTH"):
    print("\033[33m[WARN]\033[0m PASSWORD_MIN_LENGTH not set, using default value of 8")
if not os.getenv("PASSWORD_MAX_LENGTH"):
    print(
        "\033[33m[WARN]\033[0m PASSWORD_MAX_LENGTH not set, using default value of 32"
    )
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", 8))
PASSWORD_MAX_LENGTH = int(os.getenv("PASSWORD_MAX_LENGTH", 32))
USERNAME_MIN_LENGTH = int(os.getenv("USERNAME_MIN_LENGTH", 3))
USERNAME_MAX_LENGTH = int(os.getenv("USERNAME_MAX_LENGTH", 32))
if not os.getenv("USERNAME_MIN_LENGTH"):
    print("\033[33m[WARN]\033[0m USERNAME_MIN_LENGTH not set, using default value of 3")
if not os.getenv("USERNAME_MAX_LENGTH"):
    print(
        "\033[33m[WARN]\033[0m USERNAME_MAX_LENGTH not set, using default value of 32"
    )

if not os.getenv("AUTH_PORT"):
    print("\033[33m[WARN]\033[0m AUTH_PORT not set, using default value of 3121")
AUTH_PORT = int(os.getenv("AUTH_PORT", 3121))

if not os.getenv("ISSUER"):
    raise ValueError(
        format_error_message("ISSUER not set, please set it in the .env file")
    )
ISSUER = os.getenv("ISSUER")
if not os.getenv("AUTH_KEY"):
    raise ValueError(
        format_error_message("AUTH_KEY not set, please set it in the .env file")
    )
AUTH_KEY = os.getenv("AUTH_KEY")
if not os.getenv("ISSECURE"):
    print("\033[33m[WARN]\033[0m ISSECURE not set, using default value of False")
try:
    ISSECURE = bool(os.getenv("ISSECURE", False))
except ValueError:
    raise ValueError(
        format_error_message(
            "ISSECURE must be a boolean value, please set it in the .env file"
        )
    )
SOCIAL_LOGINS = os.getenv("SOCIAL_LOGINS", "")
if "google" in SOCIAL_LOGINS:
    if not os.getenv("GOOGLE_CLIENT_ID"):
        raise ValueError(
            format_error_message(
                "GOOGLE_CLIENT_ID not set, please set it in the .env file"
            )
        )
    if not os.getenv("GOOGLE_CLIENT_SECRET"):
        raise ValueError(
            format_error_message(
                "GOOGLE_CLIENT_SECRET not set, please set it in the .env file"
            )
        )
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

ISCLOUDFLARE = os.getenv("ISCLOUDFLARE", False)
if not os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"):
    print(
        "\033[33m[WARN]\033[0m ACCESS_TOKEN_EXPIRE_MINUTES not set, using default value of 60"
    )

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
DOCKER = os.getenv("DOCKER", False)
