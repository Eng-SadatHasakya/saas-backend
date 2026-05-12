from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
    override=True
)

# ✅ Standalone FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Standalone authentication microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenRequest(BaseModel):
    email: str
    role: str
    org_id: int

class TokenVerifyRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordRequest(BaseModel):
    password: str

class PasswordResponse(BaseModel):
    hashed: str

class VerifyPasswordRequest(BaseModel):
    plain: str
    hashed: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "auth-service"}

@app.post("/token/create", response_model=TokenResponse)
def create_token(request: TokenRequest):
    """Create JWT token — called by main API"""
    data = {
        "sub": request.email,
        "role": request.role,
        "org_id": request.org_id,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}

@app.post("/token/verify")
def verify_token(request: TokenVerifyRequest):
    """Verify JWT token — called by other services"""
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "email": payload.get("sub"),
            "role": payload.get("role"),
            "org_id": payload.get("org_id")
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/password/hash", response_model=PasswordResponse)
def hash_password(request: PasswordRequest):
    """Hash password — called by main API"""
    return {"hashed": pwd_context.hash(request.password)}

@app.post("/password/verify")
def verify_password(request: VerifyPasswordRequest):
    """Verify password — called by main API"""
    return {"valid": pwd_context.verify(request.plain, request.hashed)}