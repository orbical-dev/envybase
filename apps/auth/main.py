from fastapi import FastAPI, HTTPException, Response, Request
import uvicorn
import models
from config import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    AUTH_PORT,
    ISSECURE,
    AUTH_KEY,
    DOCKER,
)
from database import get_users, init_db, close_db_connection
from utils import hash_password, verify_password, create_jwt_token
from decorator import loggers_route
from oauth2 import oauth2_router
from stats import stats_router
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events for database connection.

    Initializes the database connection when the application starts and ensures it is properly closed on shutdown.
    """
    try:
        await init_db()
        yield
    except Exception as e:
        import sys
        print(f"Failed to initialize database: {e}", file=sys.stderr)
        # Do not yield here: let the exception propagate so FastAPI/Uvicorn exits with error
        raise
    finally:
        await close_db_connection()

app = FastAPI(
    title="Envybase Authentication Service",
    description="Authentication microservice for Envybase",
    version="0",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=AUTH_KEY)

# Include the routes from oauth2.py
app.include_router(oauth2_router, tags=["OAuth2"])
app.include_router(stats_router, tags=["Statistics"])

@app.get("/", summary="Health check")
@loggers_route()
async def read_root(request: Request, response: Response):
    return {"status": "healthy", "service": "auth"}


@app.get("/frontendinfo", summary="Get frontend info")
@loggers_route()
async def frontendinfo(request: Request, response: Response):
    return {
        "PASSWORD_MIN_LENGTH": PASSWORD_MIN_LENGTH,
        "PASSWORD_MAX_LENGTH": PASSWORD_MAX_LENGTH,
    }


@app.post("/login")
@loggers_route()
async def login(request: Request, response: Response, data: models.LoginData):
    """
    Authenticates a user by verifying email and password, and sets a JWT token cookie on success.
    
    Raises:
        HTTPException: If the email or password is incorrect.
    
    Returns:
        A JSON object indicating successful login and the user's email.
    """
    user = await get_users().find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )
    token = create_jwt_token({"sub": user["email"]})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=ISSECURE,
        samesite="lax",
    )
    return {"status": "success", "email": user["email"]}

@app.post("/register")
@loggers_route()
async def register(request: Request, response: Response, data: models.RegisterData):
    """
    Registers a new user with the provided email and password.
    
    Raises:
        HTTPException: If the email is already registered.
    
    Returns:
        A JSON object indicating successful registration and the user's email.
    """
    if await get_users().find_one({"email": data.email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    hashed_password = hash_password(data.password)
    user_data = {
        "email": data.email,
        "password": hashed_password,
        "created_at": str(models.datetime.datetime.utcnow()),
    }
    await get_users().insert_one(user_data)
    return {"status": "success", "email": data.email}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=AUTH_PORT,
        reload=not DOCKER,
        factory=False,
    )

