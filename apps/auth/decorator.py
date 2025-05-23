from functools import wraps
from typing import Callable
from fastapi import Request
import logging
from datetime import datetime
import pytz
import inspect
from database import get_logs
from config import ISCLOUDFLARE
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logs")

service = "auth"  # Change this, developers for your service that you're working on :(


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
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the function's signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            request = bound_args.arguments.get("request")

            if not isinstance(request, Request):
                logger.warning(
                    f"No request object found in route handler for {func.__name__}"
                )
                return await func(*args, **kwargs)

            utc_now = UTCNow()
            # Create base document once
            base_doc = {
                "method": request.method,
                "path": request.url.path,
                "client": real_ip(request),
                "timestamp": utc_now,
                "service": service,
            }

            # Log pre-execution
            logger.info(
                f"[{utc_now}]"
                f"Request: Method={request.method} "
                f"Path={request.url.path} "
                f"Client={real_ip(request)} "
            )
            await get_logs().insert_one(base_doc)

            try:
                result = await func(*args, **kwargs)
                status_code = 200
                logger.info(
                    f"[{utc_now}]"
                    f"Response: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Status={status_code} "
                    f"Client={real_ip(request)} "
                )
                await get_logs().update_one(
                    base_doc, {"$set": {"status_code": status_code}}
                )
                return result

            except Exception as e:
                error_code = 500
                match = re.search(r"ERROR:(\d+)", str(e))
                if match:
                    error_code = int(match.group(1))
                logger.error(
                    f"[{utc_now}]"
                    f"Error: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Error={str(e)} "
                    f"Client={real_ip(request)} "
                )
                await get_logs().update_one(
                    base_doc, {"$set": {"error": str(e), "status_code": error_code}}
                )
                raise

        return wrapper

    return decorator


def api_loggers_route():
    """
    Decorator for FastAPI APIRouter endpoints to log request and response details and record them in the database.
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
                return await func(*args, **kwargs)

            utc_now = UTCNow()
            # Create base document once
            base_doc = {
                "method": request.method,
                "path": request.url.path,
                "client": real_ip(request),
                "timestamp": utc_now,
                "service": service,
            }

            logger.info(
                f"[{utc_now}]"
                f"Request: Method={request.method} "
                f"Path={request.url.path} "
                f"Client={real_ip(request)} "
            )

            await get_logs().insert_one(base_doc)

            try:
                result = await func(*args, **kwargs)
                status_code = 200
                logger.info(
                    f"[{utc_now}]"
                    f"Response: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Status={status_code} "
                    f"Client={real_ip(request)} "
                )

                await get_logs().update_one(
                    base_doc, {"$set": {"status_code": status_code}}
                )
                return result

            except Exception as e:
                error_code = 500
                match = re.search(r"ERROR:(\d+)", str(e))
                if match:
                    error_code = int(match.group(1))
                logger.error(
                    f"[{utc_now}]"
                    f"Error: Method={request.method} "
                    f"Path={request.url.path} "
                    f"Error={str(e)} "
                    f"Client={real_ip(request)} "
                )
                await get_logs().update_one(
                    base_doc, {"$set": {"error": str(e), "status_code": error_code}}
                )
                raise

        return wrapper

    return decorator
