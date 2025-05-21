from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, HTTPException, Request
import config
import configparser
import jwt
from jwt import PyJWKClient
from database import get_users, get_logs
from utils import create_jwt_token, generate_username
import datetime
import pytz
import random
import httpx

ini = configparser.ConfigParser()

oauth2_router = APIRouter()


def utc_now():
    return datetime.datetime.now(pytz.UTC)


# Initialize OAuth and provider configs
oauth = OAuth()
providers = {}

# Google setup
if (
    "google" in config.SOCIAL_LOGINS
    and hasattr(config, "GOOGLE_CLIENT_ID")
    and hasattr(config, "GOOGLE_CLIENT_SECRET")
):
    providers["google"] = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "access_token_url": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "client_kwargs": {"scope": "openid email profile"},
    }
# GitHub setup
if (
    "github" in config.SOCIAL_LOGINS
    and hasattr(config, "GITHUB_CLIENT_ID")
    and hasattr(config, "GITHUB_CLIENT_SECRET")
):
    providers["github"] = {
        "client_id": config.GITHUB_CLIENT_ID,
        "client_secret": config.GITHUB_CLIENT_SECRET,
        "authorize_url": "https://github.com/login/oauth/authorize",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "userinfo_endpoint": "https://api.github.com/user",
        "email_endpoint": "https://api.github.com/user/emails",
        "client_kwargs": {"scope": "user:email"},
        "access_token_params": {"headers": {"Accept": "application/json"}},
    }

# Register providers with Authlib
for name, params in providers.items():
    opts = {
        "name": name,
        "client_id": params["client_id"],
        "client_secret": params["client_secret"],
        "authorize_url": params["authorize_url"],
        "access_token_url": params["access_token_url"],
        "userinfo_endpoint": params["userinfo_endpoint"],
        "client_kwargs": params.get("client_kwargs", {}),
    }
    if name == "github":
        opts["access_token_params"] = params["access_token_params"]
    if "server_metadata_url" in params:
        opts["server_metadata_url"] = params["server_metadata_url"]
    oauth.register(**opts)


async def log_and_raise(
    exc: Exception,
    error_type: str,
    envy_code: str,
    error_id: int = None,
    http_status: int = 400,
):
    await get_logs().insert_one(
        {
            "error": str(exc),
            "timestamp": utc_now(),
            "service": "error",
            "status": "error",
            "error_id": error_id,
            "envy_error": envy_code,
            "type": error_type,
            "status_code": http_status,
        }
    )
    if error_id:
        raise HTTPException(
            status_code=http_status,
            detail=f"{error_type}: {str(exc)}--ENVYSTART--ERROR:{envy_code};ERROR_ID:{error_id}--ENVYEND--",
        )
    else:
        raise HTTPException(
            status_code=http_status,
            detail=f"{error_type}: {str(exc)}--ENVYSTART--ERROR:{envy_code}--ENVYEND--",
        )


async def fetch_user_info(client, token, provider: str, error_id: int) -> dict:
    try:
        if provider == "github":
            access_token = token.get("access_token")
            if not access_token:
                raise ValueError("No access_token in GitHub response")
            async with httpx.AsyncClient() as c:
                headers = {"Authorization": f"Bearer {access_token}"}
                # Fetch the main profile
                user_resp = await c.get(
                    providers["github"]["userinfo_endpoint"], headers=headers
                )
                data = user_resp.json()
                # Email fallback
                if not data.get("email"):
                    emails_resp = await c.get(
                        providers["github"]["email_endpoint"], headers=headers
                    )
                    primary = next(
                        (
                            e["email"]
                            for e in emails_resp.json()
                            if e.get("primary") and e.get("verified")
                        ),
                        None,
                    )
                    data["email"] = primary
                # Map GitHub fields
                data["given_name"] = (
                    data.get("name", "").split(" ")[0] if data.get("name") else ""
                )
                data["family_name"] = (
                    " ".join(data.get("name", "").split(" ")[1:])
                    if data.get("name")
                    else ""
                )
                data["picture"] = data.get("avatar_url")
            return data
        # Google: manual JWK decode
        id_token = token.get("id_token")
        if not id_token:
            raise ValueError("No id_token in Google response")
        metadata = await client.load_server_metadata()
        jwks_uri = metadata.get("jwks_uri")
        jwk_client = PyJWKClient(jwks_uri)
        signing_key = jwk_client.get_signing_key_from_jwt(id_token)
        return jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client.client_id,
        )
    except Exception as e:
        await log_and_raise(e, "UserinfoFetchError", "300x3", error_id)


@oauth2_router.get("/oauth2/login/{provider}")
async def login_with_oauth2(request: Request, provider: str):
    if provider not in providers:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    redirect_uri = request.url_for("oauth2_callback", provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@oauth2_router.get("/oauth2/callback/{provider}")
async def oauth2_callback(request: Request, provider: str):
    if provider not in providers:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    error_id = random.randint(100000, 9999999999999)
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
        if not token:
            raise ValueError("No token received")
    except OAuthError as e:
        await log_and_raise(e, "OAuthError", "400x1", error_id)
    except Exception as e:
        await log_and_raise(e, "TokenError", "400x2", error_id)

    user_info = await fetch_user_info(client, token, provider, error_id)
    email = user_info.get("email")
    if not email:
        await log_and_raise(
            Exception("Email missing"), "MissingEmailError", "300x4", error_id
        )

    # User lookup and provider check
    user = await get_users().find_one({"email": email})
    if user:
        # Prevent login if provider differs
        if user.get("provider") != provider:
            await log_and_raise(
                Exception(
                    f"User registered with {user.get('provider')}, attempted {provider}"
                ),
                "ProviderMismatchError",
                "300x5",
                error_id,
            )
        is_new = False
    else:
        is_new = True

    # Prepare user record
    record = {
        "email": email,
        "provider": provider,
        "name": user_info.get("name", ""),
        "username": generate_username(),
        "sub": email,
        "picture": user_info.get("picture"),
        "given_name": user_info.get("given_name", ""),
        "family_name": user_info.get("family_name", ""),
        "created_at": utc_now(),
    }
    if is_new:
        await get_users().insert_one(record)
        message = f"User registered successfully with {provider.upper()}"
    else:
        message = f"User logged in successfully with {provider.upper()}"

    access_token = create_jwt_token({"sub": record["sub"]})
    return {
        "status": "success",
        "message": message,
        "access_token": access_token,
        "type": "Bearer",
        "ACCESS_TOKEN_EXPIRE_MINUTES": config.ACCESS_TOKEN_EXPIRE_MINUTES,
    }
