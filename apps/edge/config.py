import os
import dotenv

dotenv.load_dotenv()
# ANSI color constants
ERROR_COLOR = "\033[31m[ERROR]\033[0m \033[107m"
COLOR_RESET = "\033[0m"


def format_error_message(message: str) -> str:
    return f"{ERROR_COLOR}{message}{COLOR_RESET}"


if not os.getenv("MONGO_URI"):
    raise ValueError(
        format_error_message("MONGO_URI not set, please set it in the .env file"),
    )


MONGO_URI = os.getenv("MONGO_URI")
if not os.getenv("EDGE_PORT"):
    print("\033[33m[WARN]\033[0m EDGE_PORT not set, using default value of 3123")
EDGE_PORT = int(os.getenv("EDGE_PORT", 3123))
ISCLOUDFLARE = os.getenv("ISCLOUDFLARE", False)
DOCKER = os.getenv("DOCKER", False)
if DOCKER == "True":
    host = "127.0.0.1"  # Internal only because it's going to be in a Docker network
else:
    host = "0.0.0.0"
