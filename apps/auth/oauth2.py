from authlib.integrations.starlette_client import OAuth
from main import app, HTTPException

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from decorator import loggers_route

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
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

@app.get("/oauth2/login/{provider}")
@loggers_route()
async def login_with_oauth2(request, provider: str):
    """
    Redirects the user to the OAuth2 provider's login page.
    """
    redirect_uri = request.url_for("auth_callback", provider=provider)
    if provider == "google":
        return await oauth.google.authorize_redirect(request, redirect_uri)
    # elif provider == "microsoft":
    #     return await oauth.microsoft.authorize_redirect(request, redirect_uri)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

