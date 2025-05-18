from fastapi import APIRouter, HTTPException
from database import get_logs

stats_router = APIRouter()


@stats_router.get("/stats")
async def get_stats():
    """
    Retrieves authentication log entries and their total count from the database.

    Returns:
        A dictionary with the total number of authentication logs and a list of log entries,
        each containing method, path, client, timestamp, and status code (if available).

    Raises:
        HTTPException: If an error occurs while accessing or processing the database.
    """
    try:
        logs = get_logs()
        total_count = await logs.count_documents({"service": "auth"})
        log_entries = []
        async for log in logs.find({"service": "auth"}):
            log_entries.append(
                {
                    "method": log["method"],
                    "path": log["path"],
                    "client": log["client"],
                    "timestamp": log["timestamp"],
                    "status_code": log.get("status_code", None),
                }
            )
        return {
            "total_count": total_count,
            "logs": log_entries,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}",
        )
