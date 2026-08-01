from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Initialize the FastAPI application
app = FastAPI(
    title="Greenway AI Agent API",
    version="1.0.0"
)

# Add CORS Middleware to allow requests from local frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, examples=["What's the weather in Saskatoon?"])
    thread_id: str | None = Field(default=None, description="Optional thread/session ID for multi-turn conversation history")

class ChatResponse(BaseModel):
    response: str = Field(..., min_length=1, examples=["The weather in Saskatoon is ..."])
    thread_id: str | None = Field(default=None, description="New thread/session ID if a new one was created")


# Define a health check route
@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend server status."""
    return {
        "status": "ok",
        "service": "greenway_ai",
        "version": "1.0.0"
    }
