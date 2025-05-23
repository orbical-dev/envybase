from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from config import host, FUNC_PORT
from database import logs, init_db, close_db_connection, func_db
import datetime
from decorator import loggers_route  # type: ignore
from runtime import create_build_function
from models import Function
import pytz
import random


def utc_now():
    """
    Returns the current UTC time as a formatted string.

    The returned string is in the format "YYYY-MM-DD HH:MM:SS".
    """
    return datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")


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
    title="Envybase Function Service",
    description="Functions microservice for Envybase",
    version="0",
    lifespan=lifespan,
)


@app.get("/", summary="Health check")
@loggers_route()
async def read_root():
    """
    Health check endpoint for the Function service.

    Returns:
        A JSON object indicating the service is healthy.
    """
    return {"status": "healthy", "service": "function"}


@app.post("/create", summary="Create a new function function")
@loggers_route()
async def create_function(data: Function):
    """
    Creates a new function and attempts to build it.

    If a function with the same name already exists, returns an error message. On successful creation and build, returns a success message. If the build or database insertion fails, logs the error with a unique error ID and returns a message containing the error ID for support reference.

    Args:
        data: The function details to create.

    Returns:
        A dictionary indicating the result of the operation, including error information and a unique error ID if applicable.
    """
    existing_function = await func_db.find_one({"name": data.name})
    if existing_function:
        return {"status": "error", "message": "Function already exists"}

    db_insert = {
        "name": data.name,
        "code": data.code,
        "created_at": utc_now(),
    }

    try:
        await func_db.insert_one(db_insert)
        try:
            create_build_function(data.code, data.name)
            return {"status": "success", "message": "Function created successfully"}
        except Exception as build_error:
            error_id = random.randint(100000, 9999999999999)
            print(f"Build error: {build_error}")
            await logs.insert_one(
                {
                    "name": data.name,
                    "error": str(build_error),
                    "timestamp": utc_now(),
                    "status": "error",
                    "error_id": error_id,
                    "type": "build_error",
                }
            )
            return {
                "message": "Function saved but the build process failed. Please contact support and use the error ID below.",
                "error_id": error_id,
            }
    except Exception as db_error:
        error_id = random.randint(100000, 9999999999999)
        print(f"Database error: {db_error}")
        await logs.insert_one(
            {
                "name": data.name,
                "error": str(db_error),
                "timestamp": utc_now(),
                "status": "error",
                "error_id": error_id,
                "type": "db_error",
            }
        )
        return {
            "message": "Function failed to create. Please contact support and use the error ID below.",
            "error_id": error_id,
        }


if __name__ == "__main__":
    print("Starting Envybase Function Service...")
    uvicorn.run(app, host=host, port=int(FUNC_PORT))
    print("Stopping Envybase Function Service...")
