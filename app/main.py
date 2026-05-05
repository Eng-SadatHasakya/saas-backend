import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.middleware import RequestLoggingMiddleware, TenantContextMiddleware
from app.core.errors import sqlalchemy_exception_handler, general_exception_handler
from app.core.database import engine, Base

from app.routes import (
    auth, users, organizations,
    subscriptions, invitations,
    api_keys, ai, websocket, notifications
)

# ✅ Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# ✅ Create tables
Base.metadata.create_all(bind=engine)

# ✅ Create app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered, real-time, multi-tenant SaaS platform",
    version=settings.APP_VERSION,
    contact={
        "name": "Eng. Sadat Hasakya",
        "email": "hersacemusasadat@gmail.com",
        "url": "https://github.com/Eng-SadatHasakya"
    }
)

# ✅ Global middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TenantContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Global error handlers
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ✅ Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(subscriptions.router)
app.include_router(invitations.router)
app.include_router(api_keys.router)
app.include_router(ai.router)
app.include_router(notifications.router)
app.include_router(websocket.router)

# ✅ Health check
@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }