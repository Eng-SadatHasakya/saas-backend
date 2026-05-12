from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
    override=True
)

app = FastAPI(
    title="AI Service",
    description="Standalone AI microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class AIRequest(BaseModel):
    query: str
    context: dict
    org_name: str
    user_role: str

class AIResponse(BaseModel):
    response: str
    org: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai-service"}

@app.post("/query", response_model=AIResponse)
def query_ai(request: AIRequest):
    """Process AI query — called by main API"""
    try:
        system_prompt = f"""
You are an AI assistant for {request.org_name}.
The current user has the role: {request.user_role}.
Only answer based on the data provided to you.
"""
        user_prompt = f"""
Organization: {request.context.get('org_name')}
Total Users: {request.context.get('total_users')}
Plan: {request.context.get('plan')}
Users: {request.context.get('users_list')}
Pending Invites: {request.context.get('pending_invites')}
Active API Keys: {request.context.get('active_keys')}

Question: {request.query}
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
        )
        return {
            "response": response.choices[0].message.content,
            "org": request.org_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))