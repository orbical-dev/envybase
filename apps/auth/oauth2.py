from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, HTTPException, Request, status, Response
import config
import configparser
import jwt
from jwt import PyJWKClient
from database import get_users, get_logs
from utils import create_jwt_token, generate_username
import datetime
import pytz
import random

# Config Parser reads the .ini file for the user's
ini = configparser.ConfigParser()

allowed_providers = config.SOCIAL_LOGINS

oauth2_router = APIRouter()

def utc_now():
    """
    Returns the current UTC datetime as an aware datetime object.
    """
    return datetime.datetime.now(pytz.UTC)

oauth = OAuth()
if "google" in allowed_providers:
    oauth.register(
        name="google",
        client_id=config.GOOGLE_CLIENT_ID,
        client_secret=config.GOOGLE_CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        access_token_url="https://oauth2.googleapis.com/token",
        userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
        client_kwargs={"scope": "openid email profile"},
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    )

# oauth.register( # Coming soon!!!!
#    name="microsoft",
#    client_id=MICROSOFT_CLIENT_ID,
#    client_secret=MICROSOFT_CLIENT_SECRET,
#    authorize_url="https://accounts.google.com/o/oauth2/auth",
#    access_token_url="https://oauth2.googleapis.com/token",
#    userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
#    client_kwargs={"scope": "openid email profile"},
#    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",

# TODO: Add more providers


@oauth2_router.get("/oauth2/login/{provider}")
async def login_with_oauth2(request: Request, provider: str, response: Response):
    """
    Initiates the OAuth2 login flow by redirecting the user to the specified provider's authentication page.
    
    Args:
        provider: The name of the OAuth2 provider to use for authentication (e.g., "google").
    
    Raises:
        HTTPException: If the specified provider is not supported or not enabled.
        :param response:
        :param provider:
        :param request:
    """
    redirect_uri = f"http://127.0.0.1:3121/oauth2/callback/{provider}"  # request.url_for(oauth2_callback, provider=provider)

    if provider == "google" and "google" in allowed_providers:
        return await oauth.create_client("google").authorize_redirect(
            request, redirect_uri
        )
    # elif provider == "microsoft":
    #     return await oauth.microsoft.authorize_redirect(request, redirect_uri)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported provider --ENVYSTART--ERROR:300x1--ENVYEND--",
        )


@oauth2_router.get("/oauth2/callback/{provider}")
async def oauth2_callback(request: Request, provider: str, response: Response):
    """
    Handles the OAuth2 callback after user authentication, completing the login or registration process.
    
    Processes the callback from the OAuth2 provider (currently Google), retrieves and verifies the user's identity, and either registers a new user or logs in an existing one. Issues a JWT access token upon successful authentication. Returns an error response if authentication fails or required user information is missing.
    """

    if provider == "google" and "google" in allowed_providers:
        client = oauth.create_client("google")
        try:
            token = await client.authorize_access_token(request)
            if not token:
                raise HTTPException(status_code=400, detail="No token received")
        except OAuthError as oauth_err:
            error_id = random.randint(100000, 9999999999999)
            print(f"OAuth2 Error: {oauth_err}")
            await get_logs().insert_one(
                {
                    "error": str(oauth_err),
                    "timestamp": utc_now(),
                    "service": "error",
                    "status": "error",
                    "error_id": error_id,
                    "envy_error": "400",
                    "type": "oauth_error",
                    "status_code": 400,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {oauth_err.error}--ENVYSTART--ERROR:400;ERROR_ID:{error_id}--ENVYEND--",
            )
        except Exception as e:
            error_id = random.randint(100000, 9999999999999)
            print(f"Exception: {str(e)}")
            await get_logs().insert_one(
                {
                    "error": str(e),
                    "timestamp": utc_now(),
                    "service": "error",
                    "status": "error",
                    "error_id": error_id,
                    "envy_error": "400",
                    "type": "exception",
                    "status_code": 400,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to obtain access token: {str(e)}--ENVYSTART--ERROR:400;ERROR_ID:{error_id}--ENVYEND--",
            )

        try:
            id_token = token.get("id_token")
            if id_token:
                try:
                    # Fetch Google's public keys
                    jwks_url = "https://www.googleapis.com/oauth2/v3/certs"
                    jwk_client = PyJWKClient(jwks_url)
                    signing_key = jwk_client.get_signing_key_from_jwt(id_token)

                    # Decode the id_token using the public key
                    user_info = jwt.decode(
                        id_token,
                        signing_key.key,
                        algorithms=["RS256"],
                        audience=config.GOOGLE_CLIENT_ID,
                    )
                except jwt.PyJWTError as e:
                    error_id = random.randint(100000, 9999999999999)
                    print(f"Failed to decode id_token: {str(e)}")
                    await get_logs().insert_one(
                        {
                            "error": str(e),
                            "timestamp": utc_now(),
                            "service": "error",
                            "status": "error",
                            "error_id": error_id,
                            "envy_error": "300x2",
                            "type": "PyJWTError",
                            "status_code": 400,
                        }
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to decode id_token: {str(e)}--ENVYSTART--ERROR:300x2;ERROR_ID:{error_id}--ENVYEND--",
                    )
            else:
                resp = await client.get("userinfo")
                user_info = resp.json()
        except Exception as e:
            error_id = random.randint(100000, 9999999999999)
            print(f"Failed to fetch user info: {str(e)}")
            await get_logs().insert_one(
                {
                    "error": str(e),
                    "timestamp": utc_now(),
                    "service": "error",
                    "status": "error",
                    "error_id": error_id,
                    "envy_error": "300x3",
                    "type": "UserinfoFetchError",
                    "status_code": 400,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch user info: {str(e)}--ENVYSTART--ERROR:300x3;ERROR_ID:{error_id}--ENVYEND--",
            )
        email = user_info.get("email")
        if not email:
            error_id = random.randint(100000, 9999999999999)
            print("Email not provided by OAuth provider")
            await get_logs().insert_one(
                {
                    "error": "Email not provided by OAuth provider",
                    "timestamp": utc_now(),
                    "service": "error",
                    "status": "error",
                    "error_id": error_id,
                    "envy_error": "300x4",
                    "type": "MissingEmailError",
                    "status_code": 400,
                }
            )
            raise HTTPException(
                status_code=400,
                detail=f"Email not provided by OAuth provider --ENVYSTART--ERROR:300x4;ERROR_ID:{error_id}--ENVYEND--",
            )
        name = user_info.get("name", "")
        given_name = user_info.get("given_name", "")
        family_name = user_info.get("family_name", "")
        picture = user_info.get("picture")
    # elif provider == "microsoft":
    #     token = await oauth.microsoft.authorize_access_token(request)
    #     user = await oauth.microsoft.parse_id_token(request, token)
    #     return {"status": "success", "user": user}
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    user = await get_users().find_one({"email": email})
    if not user:
        user_data = {
            "email": email,
            "name": name,
            "username": generate_username(),
            "sub": email,
            "picture": picture,
            "given_name": given_name,
            "family_name": family_name,
            "created_at": utc_now(),
        }
        await get_users().insert_one(user_data)
        access_token = create_jwt_token({"sub": user_data["sub"]})
        return {
            "status": "success",
            "message": f"User registered successfully with {provider.upper()}",
            "access_token": access_token,
            "type": "Bearer",
            "ACCESS_TOKEN_EXPIRE_MINUTES": config.ACCESS_TOKEN_EXPIRE_MINUTES,
        }

    access_token = create_jwt_token({"sub": user["sub"]})
    return {
        "status": "success",
        "message": f"User logged in successfully with {provider.upper()}",
        "access_token": access_token,
        "type": "Bearer",
        "ACCESS_TOKEN_EXPIRE_MINUTES": config.ACCESS_TOKEN_EXPIRE_MINUTES,
    }
