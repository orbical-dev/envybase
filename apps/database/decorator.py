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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def real_ip(request: Request) -> str:
    """
    Get the real IP address of the client.
    If the request is from Cloudflare, use the 'CF-Connecting-IP' header.
    Otherwise, use the 'X-Real-IP' header or the remote address.
    """
    # Default fallback IP if nothing else is available
    default_ip = "0.0.0.0"

    if ISCLOUDFLARE:
        # Use Cloudflare header first, then try client host, fall back to default
        client_host = request.client.host if request.client else default_ip
        return request.headers.get("CF-Connecting-IP", client_host)
    else:
        # Use X-Real-IP header first, then try client host, fall back to default
        client_host = request.client.host if request.client else default_ip
        return request.headers.get("X-Real-IP", client_host)


def loggers_route():
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the function's signature
            sig = inspect.signature(func)

            # Get the request parameter from the bound arguments
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Get the request object
            request = bound_args.arguments.get("request")

            if not isinstance(request, Request):
                logger.warning(
                    f"No request object found in route handler for {func.__name__}"
                )
                if hasattr(func, "__await__"):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            # Get UTC time
            request_time = datetime.now(pytz.UTC)
            utc_now = request_time.strftime("%Y-%m-%d %H:%M:%S")

            # Generate a unique request ID
            request_id = str(uuid.uuid4())

            # Log pre-execution
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
                # Handle the function execution
                if hasattr(func, "__await__"):
                    response = await func(*args, **kwargs)
                else:
                    response = func(*args, **kwargs)

                # Log successful execution
                status_code = getattr(response, "status_code", 200)
                # Get a new timestamp for the response
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
                    # Update using the request_id for accurate matching
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
                # Log the error
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
