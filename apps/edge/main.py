from fastapi import FastAPI
import uvicorn
from config import EDGE_PORT
from database import edge_db
from models import EdgeFunction
import datetime

app = FastAPI(
    title="Envybase Edge function Service",
    description="Edge functions microservice for Envybase",
    version="0",
)


@app.get("/", summary="Health check")
def read_root():
    return {"status": "healthy", "service": "edge"}


@app.post("/create", summary="Create a new edge function")
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
        "created_at": datetime.datetime.now()
    }
    
if __name__ == "__main__":
    print("Starting Envybase Authentication Service...")
    uvicorn.run(app, host="0.0.0.0", port=int(EDGE_PORT))
    print("Stopping Envybase Authentication Service...")