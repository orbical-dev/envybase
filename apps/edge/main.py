from fastapi import FastAPI
import uvicorn
from config import EDGE_PORT
from database import edge_db, logs
from models import EdgeFunction
import datetime
from decorator import loggers_route # type: ignore
from runtime import create_build_function
import pytz
import random

utc_now = datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

app = FastAPI(
    title="Envybase Edge function Service",
    description="Edge functions microservice for Envybase",
    version="0",
)


@app.get("/", summary="Health check")
@loggers_route()
def read_root():
    return {"status": "healthy", "service": "edge"}


# TODO: Add authentication. NOT USER AUTH BUT UNIQUE AUTH SET IN THE .env
@app.post("/create", summary="Create a new edge function")
@loggers_route()
def create_edge_function(data: EdgeFunction):
    """
    Create a new edge function.
    """
    # Check if the function already exists
    existing_function = edge_db.find_one({"name": data.name})
    if existing_function:
        return {"status": "error", "message": "Function already exists"}
    # Insert the new function into the database
    db_insert = {
        "name": data.name,
        "code": data.code,
        "created_at": utc_now,
    }
    try:
        edge_db.insert_one(db_insert)
        try:
            create_build_function(data.code, data.name)
            return {"status": "success", "message": "Function created successfully"}
        except Exception as build_error:
            error_id = random.randint(100000, 9999999999999)
            print(f"Build error: {build_error}")
            logs.insert_one(
                {
                    "name": data.name,
                    "error": str(build_error),
                    "created_at": utc_now,
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
        logs.insert_one(
            {
                "name": data.name,
                "error": str(db_error),
                "created_at": utc_now,
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
    uvicorn.run(app, host="0.0.0.0", port=int(EDGE_PORT))
    print("Stopping Envybase edge function Service...")
