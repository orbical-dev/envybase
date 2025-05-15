from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from config import EDGE_PORT, host
from database import edge_db, logs, init_db, close_db_connection
from models import EdgeFunction
import datetime
from decorator import loggers_route  # type: ignore
from runtime import create_build_function
import pytz
import random


def utc_now():
    return datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db_connection()


app = FastAPI(
    title="Envybase Edge function Service",
    description="Edge functions microservice for Envybase",
    version="0",
    lifespan=lifespan,
)


@app.get("/", summary="Health check")
@loggers_route()
async def read_root():
    return {"status": "healthy", "service": "edge"}


@app.post("/create", summary="Create a new edge function")
@loggers_route()
async def create_edge_function(data: EdgeFunction):
    """
    Create a new edge function.
    """
    existing_function = await edge_db.find_one({"name": data.name})
    if existing_function:
        return {"status": "error", "message": "Function already exists"}

    db_insert = {
        "name": data.name,
        "code": data.code,
        "created_at": utc_now(),
    }

    try:
        await edge_db.insert_one(db_insert)
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
                    "created_at": utc_now(),
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
                "created_at": utc_now(),
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
    print("Starting Envybase edge function Service...")
    uvicorn.run(app, host=host, port=int(EDGE_PORT))
    print("Stopping Envybase edge function Service...")
