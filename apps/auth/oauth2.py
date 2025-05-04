from authlib.integrations.starlette_client import OAuth
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

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
# )
