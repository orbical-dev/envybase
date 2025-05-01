from fastapi import FastAPI, HTTPException, Response
import uvicorn
import models
from config import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, AUTH_PORT, ISSECURE
import database as db
from database import users
from utils import hash_password, verify_password, create_jwt_token, decode_jwt_token

app = FastAPI(
    title="Envybase Authentication Service",
    description="Authentication microservice for Envybase",
    version="0",
)

@app.get("/", summary="Health check")
def read_root():
    return {"status": "healthy", "service": "auth"}


@app.get("/frontendinfo", summary="Get frontend info")
def frontendinfo():
    return {
        "PASSWORD_MIN_LENGTH": PASSWORD_MIN_LENGTH,
        "PASSWORD_MAX_LENGTH": PASSWORD_MAX_LENGTH,
    }


@app.post("/login")
def login(response: Response, data: models.LoginData):
    """
    Handles user login by verifying email and password.
    Returns a success message if credentials are valid, otherwise an error message.
    """
    user = users.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token = create_jwt_token({"sub": user["sub"],})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=ISSECURE,
        samesite="lax",
    )
    return {"status": "success", "logged_in_as": user["email"]}

if __name__ == "__main__":
    print("Starting Envybase Authentication Service...")
    uvicorn.run(app, host="0.0.0.0", port=int(AUTH_PORT))
    print("Stopping Envybase Authentication Service...")
