<img width="480" height="200" alt="Envybase logo" src='https://raw.githubusercontent.com/orbical-dev/.github/refs/heads/main/Envybase%20(240%20x%20100%20px).svg'/>

<br>

[![Linting](https://github.com/orbical-dev/envybase/actions/workflows/lint.yml/badge.svg)](https://github.com/orbical-dev/envybase/actions/workflows/lint.yml)
[![Docker Build](https://github.com/orbical-dev/envybase/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/orbical-dev/envybase/actions/workflows/docker-publish.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![SDK License: MIT](https://img.shields.io/badge/SDK%20License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Envybase is an open-source Backend-as-a-Service (BaaS) platform written in Python, designed to simplify and accelerate backend development. It provides a suite of ready-to-use services for common application needs, allowing developers to focus on frontend and business logic.

## Table of Contents

*   [Features](#features)
    *   [Currently Implemented](#currently-implemented)
    *   [Planned / Roadmap](#planned--roadmap)
*   [Technology Stack](#technology-stack)
*   [Project Structure](#project-structure)
*   [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Cloning the Repository](#cloning-the-repository)
    *   [Configuration](#configuration)
    *   [Running the Services](#running-the-services)
*   [Using the Python SDK (envypy)](#using-the-python-sdk-envypy)
*   [Contributing](#contributing)
*   [License](#license)

## Features

### Currently Implemented

*   **User Authentication & Authorization (`apps/auth`):**
    *   Email/Password registration and login.
    *   JWT-based session management.
    *   OAuth2 integration (currently configured for Google).
    *   Request logging.
*   **NoSQL Document Database Integration:**
    *   Utilizes MongoDB for data persistence across services.
*   **Edge Function Management (`apps/edge`):**
    *   API for creating and storing user-defined serverless functions (code and name).
    *   *(Execution of functions is a planned feature).*

### Planned / Roadmap

*   **S3-Compatible Object Storage:** For flexible file storage.
*   **Real-time Database Features:** Leveraging technologies like WebSockets or Redis Pub/Sub.
*   **Expanded Edge Function Capabilities:**
    *   Secure execution environments.
    *   Triggers (HTTP, database events, cron).
    *   Version management.
*   **More OAuth Providers:** Support for GitHub, Facebook, etc.
*   **Admin Dashboard/UI:** For managing users, data, and services.
*   **Enhanced SDK:** More comprehensive functionality and documentation for `envypy`.

## Technology Stack

*   **Backend Framework:** Python, [FastAPI](https://fastapi.tiangolo.com/)
*   **Database:** [MongoDB](https://www.mongodb.com/)
*   **Caching/Message Broker (dependencies):** [Redis](https://redis.io/) (used by `docker-compose.yaml`)
*   **Authentication:** JWT ([PyJWT](https://pyjwt.readthedocs.io/)), Password Hashing ([bcrypt](https://pypi.org/project/bcrypt/)), OAuth ([Authlib](https://authlib.org/))
*   **Data Validation:** [Pydantic](https://pydantic-docs.helpmanual.io/)
*   **Containerization:** [Docker](https://www.docker.com/), Docker Compose
*   **Python SDK:** `envypy`
*   **CI/CD:** GitHub Actions
*   **Linting:** [Ruff](https://beta.ruff.rs/docs/)

## Getting Started

### Prerequisites

*   [Git](https://git-scm.com/)
*   [Python](https://www.python.org/downloads/) (3.9+ recommended, check individual app `requirements.txt`)
*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### Cloning the Repository

```bash
git clone https://github.com/orbical-dev/envybase.git
cd envybase
```

### Configuration

Both the `auth` and `edge` services require environment variables for configuration. You'll need to create a `.env` file in each application's directory (`apps/auth/.env` and `apps/edge/.env`).

**1. For `apps/auth/.env`:**

```env
# Example apps/auth/.env
MONGO_URI=mongodb://localhost:27017/
REDIS_HOST=localhost
REDIS_PORT=6379

# IMPORTANT: Generate a strong, random secret key
AUTH_KEY=your_strong_secret_jwt_key
ISSUER=envybase.local # Or your domain

# Password Policy (defaults are shown)
# PASSWORD_MIN_LENGTH=8
# PASSWORD_MAX_LENGTH=32
# USERNAME_MIN_LENGTH=3
# USERNAME_MAX_LENGTH=32

# OAuth2 - Google (Optional, get from Google Cloud Console)
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret

# Service Port
AUTH_PORT=8005
ISSECURE=False # Set to True if using HTTPS
ISCLOUDFLARE=False # Set to True if behind Cloudflare for real IP
```

**2. For `apps/edge/.env`:**

```env
# Example apps/edge/.env
MONGO_URI=mongodb://localhost:27017/

# Service Port
EDGE_PORT=8006 # Or your desired port
```

### Running the Services

1.  **Start Dependencies (MongoDB & Redis):**
    Use Docker Compose to start the required database and caching services.

    ```bash
    docker-compose up -d
    ```

2.  **Set up Python Virtual Environments & Install Dependencies for Each App:**

    *   **Auth Service:**
        ```bash
        cd apps/auth
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        pip install -r requirements.txt
        cd ../..
        ```

    *   **Edge Service:**
        ```bash
        cd apps/edge
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        pip install -r requirements.txt
        cd ../..
        ```

3.  **Run the Applications:**
    Open two separate terminal windows/tabs.

    *   **Terminal 1: Run Auth Service**
        ```bash
        cd apps/auth
        source venv/bin/activate # If not already active
        uvicorn main:app --reload --port $(grep AUTH_PORT .env | cut -d '=' -f2)
        # Or manually: uvicorn main:app --reload --port 8005
        ```
        The Auth service should now be running (default: `http://localhost:8005`).

    *   **Terminal 2: Run Edge Service**
        ```bash
        cd apps/edge
        source venv/bin/activate # If not already active
        uvicorn main:app --reload --port $(grep EDGE_PORT .env | cut -d '=' -f2)
        # Or manually: uvicorn main:app --reload --port 8006
        ```
        The Edge service should now be running (e.g., `http://localhost:8006`).

## Using the Python SDK (envypy)

The `envypy` SDK is still under active development. It aims to provide a convenient way to interact with Envybase services from your Python applications.

**Installation (once published or from source):**
```bash
# From PyPI (when available)
pip install envypy

# Or install locally for development
cd sdk/
pip install -e .
```

**Basic Usage (Conceptual Example):**
```python
from envypy import envypy
# from envypy.edge_functions import EdgeFunctions # Assuming this structure

# Initialize the main client (replace with your Envybase auth service URL)
# This part of the SDK might be for general API calls or user context
# envy_client = envypy(api_url="http://localhost:8005", api_key="USER_JWT_TOKEN_IF_NEEDED")

# Example: Interacting with Edge Functions (structure may evolve)
# edge_service_url = "http://localhost:8006" # Replace with your edge service URL
# edge_functions_client = EdgeFunctions(api_key="YOUR_API_KEY_OR_USER_TOKEN", base_url=edge_service_url)

# try:
#     # Assuming a method to create an edge function
#     response = edge_functions_client.create(name="myTestFunction", code="def handler(event, context):\n  return {'message': 'Hello from Envybase Edge!'}")
#     print("Function created:", response)
# except Exception as e:
#     print("Error:", e)

print("Envybase SDK is under development. Check sdk/README.md for more updates.")
```
*Note: The SDK's API and structure are subject to change. Refer to the `sdk/README.md` and source code for the latest details.*

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, documentation improvements, or code contributions, please feel free to:

1.  **Open an issue:** Discuss the change you wish to make via the issue tracker.
2.  **Fork the repository:** Create your own copy.
3.  **Create a feature branch:** `git checkout -b feature/AmazingFeature`
4.  **Commit your changes:** `git commit -m 'Add some AmazingFeature'`
5.  **Push to the branch:** `git push origin feature/AmazingFeature`
6.  **Open a Pull Request:** Submit your changes for review.

Please ensure your code adheres to the project's linting standards (Ruff is used, configured in `pyproject.toml` if applicable, or run `ruff check . --fix`).

## License

The Envybase core platform (contents of the `apps/` directory and other root project files) is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

The Python SDK (`envypy`, located in the `sdk/` directory) is licensed under the **MIT License** - see the [sdk/LICENSE](sdk/LICENSE) file for details. This allows for more permissive use of the client library in various projects.