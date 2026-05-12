from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(
    title="API Gateway",
    description="Routes requests to microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8002"),
    "ai": os.getenv("AI_SERVICE_URL", "http://localhost:8003"),
    "main": os.getenv("MAIN_SERVICE_URL", "http://localhost:8000"),
}

@app.get("/health")
async def health():
    """Check health of all services"""
    statuses = {}
    async with httpx.AsyncClient() as client:
        for service, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=3)
                statuses[service] = response.json()
            except Exception:
                statuses[service] = {"status": "unreachable"}
    return {"gateway": "healthy", "services": statuses}

@app.get("/services")
def list_services():
    return {"services": SERVICES}