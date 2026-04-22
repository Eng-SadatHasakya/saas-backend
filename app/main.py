import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, users, organizations, subscriptions, invitations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaaS Backend API",
    description="Multi-tenant SaaS backend with organization isolation",
    version="1.0.0",
    contact={
        "name": "Eng. Sadat Hasakya",
        "email": "hersacemusasadat@gmail.com",
        "url": "https://github.com/Eng-SadatHasakya"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(organizations.router)
app.include_router(subscriptions.router)
app.include_router(invitations.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "SaaS Backend API is running", "version": "1.0.0"}