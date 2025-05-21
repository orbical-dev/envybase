from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import uvicorn
from config import DATABASE_PORT, host
from database import database_db, logs, init_db, close_db_connection
from models import Document, Query, Update, Delete
import pytz
import datetime
import random
from decorator import loggers_route  # type: ignore


def get_utc_now():
    return datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db_connection()


app = FastAPI(
    title="Envybase Database Service",
    description="Database microservice for Envybase",
    version="0",
    lifespan=lifespan,
)


@app.get("/", summary="Health check")
@loggers_route()
async def read_root(request: Request):
    return {"status": "healthy", "service": "database"}


@app.post("/insert", summary="Insert a new document into the database")
@loggers_route()
async def insert(data: Document, request: Request):
    try:
        db_insert = data.model_dump()
        await database_db.insert_one(db_insert)
        return {"status": "success", "message": "Document inserted successfully"}
    except Exception as e:
        error_id = random.randint(100000, 9999999999999)
        await logs.insert_one(
            {
                "name": data.name,
                "error": str(e),
                "created_at": get_utc_now(),
                "status": "error",
                "error_id": error_id,
                "type": "insert_error",
            }
        )
        raise HTTPException(
            status_code=500, detail=f"Error during database insertion: {str(e)}"
        )


@app.post("/select", summary="Select a document from the database")
@loggers_route()
async def select(data: Query, request: Request):
    query = data.query
    try:
        cursor = database_db.find(query)
        result_list = []
        async for doc in cursor:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            result_list.append(doc)
        return {"status": "success", "data": result_list}
    except Exception as e:
        error_id = random.randint(100000, 9999999999999)
        log_name = getattr(data, "name", "N/A")
        await logs.insert_one(
            {
                "name": log_name,
                "query_attempted": query,
                "error": str(e),
                "created_at": get_utc_now(),
                "status": "error",
                "error_id": error_id,
                "type": "select_error",
            }
        )
        raise HTTPException(
            status_code=500, detail=f"Error during database selection: {str(e)}"
        )


@app.post("/delete", summary="Delete a document from the database")
@loggers_route()
async def delete(data: Delete, request: Request):
    query = data.query
    try:
        result = await database_db.delete_one(query)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="No document found to delete")
        return {"status": "success"}
    except Exception as e:
        error_id = random.randint(100000, 9999999999999)
        log_name = getattr(data, "name", "N/A")
        await logs.insert_one(
            {
                "name": log_name,
                "query_attempted": query,
                "error": str(e),
                "created_at": get_utc_now(),
                "status": "error",
                "error_id": error_id,
                "type": "delete_error",
            }
        )
        raise HTTPException(
            status_code=500, detail=f"Error during database deletion: {str(e)}"
        )


@app.post("/update", summary="Update a document from the database")
@loggers_route()
async def update(data: Update, request: Request):
    query = data.query
    update_payload = data.update
    try:
        result = await database_db.update_one(query, {"$set": update_payload})
        return {
            "status": "success",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
        }
    except Exception as e:
        error_id = random.randint(100000, 9999999999999)
        log_name = getattr(data, "name", "N/A")
        await logs.insert_one(
            {
                "name": log_name,
                "query_attempted": query,
                "update_payload_attempted": update_payload,
                "error": str(e),
                "created_at": get_utc_now(),
                "status": "error",
                "error_id": error_id,
                "type": "update_error",
            }
        )
        raise HTTPException(
            status_code=500, detail=f"Error during database update: {str(e)}"
        )


if __name__ == "__main__":
    print("Starting Envybase Database Service...")
    uvicorn.run(app, host=host, port=int(DATABASE_PORT))
    print("Stopping Envybase Database Service...")
