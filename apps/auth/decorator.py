from functools import wraps
from typing import Callable
from fastapi import Request
import logging
from datetime import datetime
import pytz
import inspect
from database import logs
from config import ISCLOUDFLARE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            utc_now = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

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
                }
            )

            try:
                # Handle the function execution
                if hasattr(func, "__await__"):
                    response = await func(*args, **kwargs)
                else:
                    response = func(*args, **kwargs)

                # Log successful execution
                status_code = getattr(response, "status_code", 200)
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
                    },
                    {"$set": {"error": str(e)}},
                )
                raise

        return wrapper

    return decorator
