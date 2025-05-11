from fastapi import FastAPI, HTTPException
import uvicorn
from config import DATABASE_PORT
from database import database_db, logs
from models import Document, Query
import pytz
import datetime
import random
from decorator import loggers_route # type: ignore

utc_now = datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

app = FastAPI(
    title="Envybase Database Service",
    description="Database microservice for Envybase",
    version="0",
)


@app.get("/", summary="Health check")
@loggers_route()
def read_root():
    return {"status": "healthy", "service": "database"}


@app.post("/insert", summary="Insert a new document into the database")
@loggers_route()
def insert(data: Document):
    """
    Insert a new document into the database.
    """
    # Insert the new function into the database
    db_insert = data

    db_insert = data.model_dump() # Convert Pydantic model to dict for MongoDB
    try:
        database_db.insert_one(db_insert)
        return {"status": "success", "message": "Document inserted successfully"}
    except Exception as e:
        error_id = random.randint(100000, 9999999999999)
        print(f"Insert error: {e}")
        logs.insert_one(
            {
                "name": data.name,
                "error": str(e),
                "created_at": utc_now,
                "status": "error",
                "error_id": error_id,
                "type": "insert_error",
            }
        )
        return {"status": "error", "message": str(e)}
@app.post("/select", summary="Select a document from the database")
@loggers_route()
def select(data: Query):
    """
    Select a document from the database.
    """
    query = data.query
    try:
        cursor = database_db.find(query)
        result_list = []
        for doc in cursor:
            if "_id" in doc: # Ensure _id exists
                doc["_id"] = str(doc["_id"]) # Convert ObjectId to string for JSON serialization
            result_list.append(doc)
        return {"status": "success", "data": result_list}
    except Exception as e:
        error_id = random.randint(100000, 9999999999999)
        # Safely access data.name for logging, assuming Query model might have it as Optional
        log_name = data.name if hasattr(data, 'name') and data.name is not None else "N/A"
        print(f"Select error: {e}")
        logs.insert_one(
            {
                "name": log_name,
                "query_attempted": query, # Log the query that failed
                "error": str(e),
                "created_at": utc_now, # Use dynamic timestamp function
                "status": "error",
                "error_id": error_id,
                "type": "select_error",
            }
        )
        # Use HTTPException for consistency in error responses
        raise HTTPException(status_code=500, detail=f"Error during database selection: {str(e)}")


if __name__ == "__main__":
    print("Starting Envybase Database Service...")
    uvicorn.run(app, host="0.0.0.0", port=int(DATABASE_PORT))
    print("Stopping Envybase Database Service...")


