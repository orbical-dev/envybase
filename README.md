<img width="480" height="200" alt="Envybase logo" src='https://raw.githubusercontent.com/orbical-dev/.github/refs/heads/main/Envybase%20(240%20x%20100%20px).svg'/>

<br>

> **⚠️ STATUS:** Do not use at all!

[![Linting](https://github.com/orbical-dev/envybase/actions/workflows/lint.yml/badge.svg)](https://github.com/orbical-dev/envybase/actions/workflows/lint.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
![Project License](https://img.shields.io/github/license/orbical-dev/envybase)
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
        *   [Option 1: Using Docker Compose (Recommended for Full Stack)](#option-1-using-docker-compose-recommended-for-full-stack)
        *   [Option 2: Manual Local Development (Linux/WSL for Apps, Docker for Dependencies)](#option-2-manual-local-development-linuxwsl-for-apps-docker-for-dependencies)
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
*   **Edge Function Management & Initial Runtime (`apps/edge`):**
    *   API for creating and storing user-defined serverless functions (code and name).
    *   Basic runtime capability using Docker to execute provided Python code (via `apps/edge/runtime.py`).

### Planned / Roadmap

*   **S3-Compatible Object Storage:** For flexible file storage.
*   **Real-time Database Features:** Leveraging technologies like WebSockets or Redis Pub/Sub.
*   **Expanded Edge Function Capabilities:**
    *   More robust and secure execution environments.
    *   Dependency management for edge functions.
    *   Triggers (HTTP, database events, cron).
    *   Version management.
*   **More OAuth Providers:** Support for GitHub, Facebook, etc.
*   **Admin Dashboard/UI:** For managing users, data, and services.
*   **Enhanced SDK:** More comprehensive functionality and documentation for `envypy`.

## Technology Stack

*   **Backend Framework:** Python, [FastAPI](https://fastapi.tiangolo.com/)
*   **Database:** [MongoDB](https://www.mongodb.com/)
*   **Caching/Message Broker (dependencies):** [Redis](https://redis.io/)
*   **Authentication:** JWT ([PyJWT](https://pyjwt.readthedocs.io/)), Password Hashing ([bcrypt](https://pypi.org/project/bcrypt/)), OAuth ([Authlib](https://authlib.org/))
*   **Data Validation:** [Pydantic](https://pydantic-docs.helpmanual.io/)
*   **Containerization & Edge Runtime:** [Docker](https://www.docker.com/), Docker Compose, Python Docker SDK
*   **Python SDK:** `envypy`
*   **CI/CD:** GitHub Actions (Linting)
*   **Linting:** [Ruff](https://beta.ruff.rs/docs/)

## Project Structure

```
envybase/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       └── lint.yml
├── apps/                       # Core microservices
│   ├── auth/                   # Authentication and User Management service
│   │   ├── Dockerfile          # Dockerfile for the auth app
│   │   ├── main.py             # FastAPI app for auth
│   │   ├── models.py           # Pydantic models
│   │   ├── utils.py            # Auth helpers (JWT, hashing)
│   │   ├── database.py         # MongoDB connection
│   │   ├── config.py           # Environment configuration
│   │   └── requirements.txt
│   └── edge/                   # Edge Functions service
│       ├── Dockerfile          # Dockerfile for the edge app
│       ├── main.py             # FastAPI app for edge functions
│       ├── models.py           # Pydantic models
│       ├── runtime.py          # Core logic for building/running edge functions in Docker
│       ├── database.py         # MongoDB connection
│       ├── config.py           # Environment configuration
│       └── requirements.txt
├── sdk/                        # Python SDK (envypy)
│   ├── src/envypy/
│   ├── build.sh
│   ├── pyproject.toml
│   └── README.md
├── .gitignore
├── docker-compose.yaml         # Defines and runs all services (apps, MongoDB, Redis)
├── LICENSE                     # Main project license (GPLv3)
└── README.md                   # This file
```

## Getting Started

### Prerequisites

*   [Git](https://git-scm.com/)
*   [Python](https://www.python.org/downloads/) (3.9+ recommended, Python 3.13 used in Dockerfiles)
*   [Python Virtual Environment](https://docs.python.org/3/library/venv.html) (for manual local development)
*   [A distro of Linux](https://www.linux.org/) (or WSL Ubuntu on Windows, especially if doing manual setup)
*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### Cloning the Repository

```bash
git clone https://github.com/orbical-dev/envybase.git
cd envybase
```

### Configuration

Environment variables are crucial.
*   When using **Docker Compose (Option 1 below)**, most configurations are set directly in `docker-compose.yaml`. You'll primarily need to update placeholder values like `AUTH_KEY` and `ISSUER` there.
*   When running apps **manually with `uvicorn` (Option 2 below)**, you'll need `.env` files in each app's directory (`apps/auth/.env` and `apps/edge/.env`).

**Example `.env` files for manual local development (Option 2):**

**1. For `apps/auth/.env`:**
    (Port `3121` aligns with `docker-compose.yaml` and new default)
```env
# Example apps/auth/.env
MONGO_URI=mongodb://localhost:27017/  # Assumes MongoDB running locally
REDIS_HOST=localhost                 # Assumes Redis running locally
REDIS_PORT=6379

# IMPORTANT: Generate a strong, random secret key
AUTH_KEY=your_strong_secret_jwt_key_for_local_dev
ISSUER=envybase.local.dev # Or your local domain

# Password Policy (defaults are shown)
# PASSWORD_MIN_LENGTH=8
# PASSWORD_MAX_LENGTH=32
# USERNAME_MIN_LENGTH=3
# USERNAME_MAX_LENGTH=32

# OAuth2 - Google (Optional, get from Google Cloud Console)
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret

# Service Port
AUTH_PORT=3121
ISSECURE=False # Set to True if using HTTPS
ISCLOUDFLARE=False # Set to True if behind Cloudflare for real IP
```

**2. For `apps/edge/.env`:**
    (Port `3123` aligns with `docker-compose.yaml`)
```env
# Example apps/edge/.env
MONGO_URI=mongodb://localhost:27017/ # Assumes MongoDB running locally

# Service Port
EDGE_PORT=3123
ISCLOUDFLARE=False
```

### Running the Services

Choose one of the following methods:

#### Option 1: Using Docker Compose (Recommended for Full Stack)

This method will build and run the `auth` app, `edge` app, `mongodb`, and `redis` services together.

1.  **Review `docker-compose.yaml`:**
    Before running, open `docker-compose.yaml` and ensure the environment variables (especially `AUTH_KEY` and `ISSUER` for the `auth` service) are set to secure values if you plan to expose this setup. For initial local testing, the placeholders might be fine, but **do not use default/placeholder secrets in production.**

2.  **Build and Run All Services:**
    From the root of the `envybase` directory:
    ```bash
    docker-compose up --build
    ```
    To run in detached mode (in the background):
    ```bash
    docker-compose up --build -d
    ```

    *   Auth service will be available at `http://localhost:3121`
    *   Edge service will be available at `http://localhost:3123`
    *   MongoDB will be available at `mongodb://localhost:27017` (from your host machine)
    *   Redis will be available at `redis://localhost:6379` (from your host machine)

3.  **To Stop Services:**
    ```bash
    docker-compose down
    ```

#### Option 2: Manual Local Development (Linux/WSL for Apps, Docker for Dependencies)

This method is for developers who want to run the Python app code directly on their machine (e.g., for faster reloading with `uvicorn` or easier debugging) while still using Docker for MongoDB and Redis.

1.  **Start Dependencies (MongoDB & Redis) with Docker Compose:**
    If you only want to run the dependencies with Docker Compose:
    ```bash
    docker-compose up -d mongodb redis
    ```
    This will start MongoDB on port 27017 and Redis on port 6379.
    Alternatively, you can install and run MongoDB and Redis natively on your Linux/WSL system if you prefer, ensuring they listen on `0.0.0.0` or `localhost`.

2.  **Set up Python Virtual Environments & Install Dependencies for Each App:**
    Make sure you have created the `.env` files as described in the "Configuration" section above.

    *   **Auth Service:**
        ```bash
        cd apps/auth
        python -m venv venv
        source venv/bin/activate  # On Windows (if not using WSL): venv\Scripts\activate
        pip install -r requirements.txt
        cd ../..
        ```

    *   **Edge Service:**
        ```bash
        cd apps/edge
        python -m venv venv
        source venv/bin/activate  # On Windows (if not using WSL): venv\Scripts\activate
        pip install -r requirements.txt
        cd ../..
        ```

3.  **Run the Applications:**
    Open two separate terminal windows/tabs.

    *   **Terminal 1: Run Auth Service**
        (Ensure `apps/auth/.env` is configured and MongoDB/Redis are accessible)
        ```bash
        cd apps/auth
        source venv/bin/activate # If not already active
        uvicorn main:app --reload --port $(grep AUTH_PORT .env | cut -d '=' -f2 | head -n 1)
        # Or manually: uvicorn main:app --reload --port 3121
        ```
        The Auth service should now be running (default: `http://localhost:3121`).

    *   **Terminal 2: Run Edge Service**
        (Ensure `apps/edge/.env` is configured and MongoDB is accessible)
        ```bash
        cd apps/edge
        source venv/bin/activate # If not already active
        uvicorn main:app --reload --port $(grep EDGE_PORT .env | cut -d '=' -f2 | head -n 1)
        # Or manually: uvicorn main:app --reload --port 3123
        ```
        The Edge service should now be running (e.g., `http://localhost:3123`).
        *Note: The Edge service (`runtime.py`) will attempt to use the Docker daemon on your host. Ensure Docker is running and accessible.*

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
# envy_client = envypy(api_url="http://localhost:3121", api_key="USER_JWT_TOKEN_IF_NEEDED")

# Example: Interacting with Edge Functions (structure may evolve)
# edge_service_url = "http://localhost:3123" # Replace with your edge service URL
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

Please ensure your code adheres to the project's linting standards (Ruff is used, run `ruff check . --fix` from the project root).

## License

The Envybase core platform (contents of the `apps/` directory and other root project files) is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

The Python SDK (`envypy`, located in the `sdk/` directory) is licensed under the **MIT License** - see the [sdk/LICENSE](sdk/LICENSE) file for details. This allows for more permissive use of the client library in various projects.
