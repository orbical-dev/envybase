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
from database import users, init_db, close_db_connection
from utils import hash_password, verify_password, create_jwt_token
from decorator import loggers_route
from oauth2 import oauth2_router
from stats import stats_router
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for FastAPI app lifespan events.
    Initializes the database connection when the application starts and closes it upon shutdown.
    """
    await init_db()
    yield
    await close_db_connection()

app = FastAPI(
    title="Envybase Authentication Service",
    description="Authentication microservice for Envybase",
    version="0",
    lifespan=lifespan
)

app.add_middleware(SessionMiddleware, secret_key=AUTH_KEY)

# Include the routes from oauth2.py and stats.py
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
    """
    user = await users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password --ENVYSTART--ERROR:300x6--ENVYEND--",
        )
    token = create_jwt_token({"sub": user["sub"]})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=ISSECURE,
        samesite="lax",
    )
    return {"status": "success", "logged_in_as": user["email"]}


@app.post("/register")
@loggers_route()
async def register(request: Request, response: Response, data: models.RegisterData):
    """
    Registers a new user with the provided email, password, name, and username.
    Raises:
        HTTPException: If the email is already registered.
    """
    if await users.find_one({"email": data.email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered --ENVYSTART--ERROR:300x5--ENVYEND--",
        )
    hashed_password = hash_password(data.password)
    user_data = {
        "email": data.email,
        "password": hashed_password,
        "name": data.name,
        "username": data.username,
        "sub": data.email,
    }
    await users.insert_one(user_data)
    return {"status": "success", "message": "User registered successfully"}


host = "0.0.0.0" if DOCKER else "127.0.0.1"

if __name__ == "__main__":
    print("Starting Envybase Authentication Service...")
    uvicorn.run(app, host=host, port=int(AUTH_PORT))
    print("Stopping Envybase Authentication Service...")
