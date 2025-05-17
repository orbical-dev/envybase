from functools import wraps
from typing import Callable
from fastapi import Request
import logging
from datetime import datetime
import pytz
import inspect
from database import logs
from config import ISCLOUDFLARE
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logs")


def UTCNow():
    """
    Returns the current UTC time.
    """
    return datetime.now(pytz.UTC)


def real_ip(request: Request) -> str:
    """
    Get the real IP address of the client.
    If the request is from Cloudflare, use the 'CF-Connecting-IP' header.
    Otherwise, use the 'X-Real-IP' header or the remote address.
    """
    if ISCLOUDFLARE:
        return request.headers.get("CF-Connecting-IP", request.client.host)
    return request.headers.get("X-Real-IP", request.client.host)


def loggers_route():
    """
    Decorator for FastAPI route handlers that logs request and response details and records them in the database.

    Logs the HTTP method, path, client IP, and timestamp for each request. On successful execution, updates the log entry with a status code. On exception, logs the error, extracts an error code from the exception message if present, updates the log entry with error details, and re-raises the exception.
    """

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
            response = bound_args.arguments.get("response")

            if not isinstance(request, Request):
                logger.warning(
                    f"No request object found in route handler for {func.__name__}"
                )
                if hasattr(func, "__await__"):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            # Get UTC time
            # Log pre-execution
            logger.info(
                f"[{UTCNow()}]"
                f"Request: Method={request.method} "
                f"Path={request.url.path} "
                f"Client={real_ip(request)} "
            )
            await logs.insert_one(
                {
                    "method": request.method,
                    "path": request.url.path,
                    "client": real_ip(request),
                    "timestamp": UTCNow(),
                    "service": "auth",
                }
            )

            try:
                # Handle the function execution
                if hasattr(func, "__await__"):
                    response = await func(*args, **kwargs)
                else:
                    response = func(*args, **kwargs)

                # Log successful execution
                status_code = 200
                logger.info(
                    f"[{UTCNow()}]"
                    f"Response: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Status={status_code} "
                    f"Client={real_ip(request)} "
                )
                logs.update_one(
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "client": real_ip(request),
                        "timestamp": UTCNow(),
                        "service": "auth",
                    },
                    {"$set": {"status_code": status_code}},
                )

                return response

            except Exception as e:
                # Log the error
                logger.error(
                    f"[{UTCNow()}]"
                    f"Error: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Error={str(e)} "
                    f"Client={real_ip(request)} "
                )
                match = re.search(r"ERROR:([0-9x]+)", str(e))
                error_code = match.group(1) if match else "500"
                print(error_code)
                logs.update_one(
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "client": real_ip(request),
                        "timestamp": UTCNow(),
                        "service": "auth",
                    },
                    {"$set": {"error": str(e), "status_code": error_code}},
                )
                raise

        return wrapper

    return decorator


def api_loggers_route():
    """
    Creates a decorator for async FastAPI route handlers to log request and response details, including errors, and record them in the database.

    The decorator logs the HTTP method, path, client IP, and timestamp for each request. It updates the log entry with the response status code on success or with error details and a 500 status code on exception. If no valid Request object is found, the original function is called without logging.
    """

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
                return await func(*args, **kwargs)

            # Get UTC time
            utc_now = datetime.now(pytz.UTC)

            # Log pre-execution
            logger.info(
                f"[{utc_now}]"
                f"Request: Method={request.method} "
                f"Path={request.url.path} "
                f"Client={real_ip(request)} "
            )
            logs.insert_one(
                {
                    "method": request.method,
                    "path": request.url.path,
                    "client": real_ip(request),
                    "timestamp": utc_now,
                    "service": "auth",
                }
            )

            try:
                # Handle the function execution
                response = await func(*args, **kwargs)

                # Log successful execution
                status_code = (
                    response.status_code if hasattr(response, "status_code") else 200
                )
                logger.info(
                    f"[{utc_now}]"
                    f"Response: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Status={status_code} "
                    f"Client={real_ip(request)} "
                )
                logs.update_one(
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "client": real_ip(request),
                        "timestamp": utc_now,
                        "service": "auth",
                    },
                    {"$set": {"status_code": status_code}},
                )

                return response

            except Exception as e:
                # Log the error
                logger.error(
                    f"[{utc_now}]"
                    f"Error: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Error={str(e)} "
                    f"Client={real_ip(request)} "
                )
                logs.update_one(
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "client": real_ip(request),
                        "timestamp": utc_now,
                        "service": "auth",
                    },
                    {"$set": {"error": str(e), "status_code": 500}},
                )
                raise

        return wrapper

    return decorator
