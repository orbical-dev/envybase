from functools import wraps
from typing import Callable
from fastapi import Request
import logging
from datetime import datetime
import pytz
import inspect
from database import logs
from config import ISCLOUDFLARE
import uuid
import asyncio  # <-- Add this import


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def real_ip(request: Request) -> str:
    """
    Determines the client's real IP address from a FastAPI Request.

    If Cloudflare integration is enabled, returns the IP from the 'CF-Connecting-IP' header; otherwise, uses the 'X-Real-IP' header or falls back to the remote address.
    """
    default_ip = "0.0.0.0"

    if ISCLOUDFLARE:
        client_host = request.client.host if request.client else default_ip
        return request.headers.get("CF-Connecting-IP", client_host)
    else:
        client_host = request.client.host if request.client else default_ip
        return request.headers.get("X-Real-IP", client_host)


def loggers_route():
    """
    Creates a decorator for FastAPI route handlers that logs request and response details,
    including client IP, method, path, status code, and timestamps, and stores them
    asynchronously in a database.

    The decorator generates a unique request ID for each call, logs metadata before and after
    the route handler executes, and updates the log entry with response or error information.
    If the route handler raises an exception, the error is logged and recorded in the database.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            request = bound_args.arguments.get("request")

            if not isinstance(request, Request):
                logger.warning(
                    f"No request object found in route handler for {func.__name__}"
                )
                # Use asyncio.iscoroutinefunction here instead of hasattr
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            request_time = datetime.now(pytz.UTC)
            utc_now = request_time.strftime("%Y-%m-%d %H:%M:%S")
            request_id = str(uuid.uuid4())

            logger.info(
                f"[{request_id}][{utc_now}]"
                f"Request: Method={request.method} "
                f"Path={request.url.path} "
                f"Client={real_ip(request)} "
            )
            try:
                await logs.insert_one(
                    {
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "client": real_ip(request),
                        "timestamp": utc_now,
                    }
                )
            except Exception as db_error:
                logger.error(f"[{request_id}] Failed to insert log: {db_error}")
            try:
                # Properly detect coroutine function here
                if asyncio.iscoroutinefunction(func):
                    response = await func(*args, **kwargs)
                else:
                    response = func(*args, **kwargs)

                status_code = getattr(response, "status_code", 200)
                response_time = datetime.now(pytz.UTC)
                response_utc = response_time.strftime("%Y-%m-%d %H:%M:%S")

                logger.info(
                    f"[{request_id}][{response_utc}]"
                    f"Response: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Status={status_code} "
                    f"Client={real_ip(request)} "
                )
                try:
                    await logs.update_one(
                        {"request_id": request_id},
                        {
                            "$set": {
                                "status_code": status_code,
                                "response_time": response_utc,
                                "duration_ms": (
                                    response_time - request_time
                                ).total_seconds()
                                * 1000,
                            }
                        },
                    )
                except Exception as db_error:
                    logger.error(f"[{request_id}] Failed to update log: {db_error}")

                return response
            except Exception as e:
                logger.error(
                    f"[{request_id}][{utc_now}]"
                    f"Error: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Error={str(e)} "
                    f"Client={real_ip(request)} "
                )
                try:
                    await logs.update_one(
                        {"request_id": request_id},
                        {"$set": {"error": str(e)}},
                    )
                except Exception as db_error:
                    logger.error(
                        f"[{request_id}] Failed to update error log: {db_error}"
                    )
                raise

        return wrapper

    return decorator
