from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent import root_agent

# Load environment variables from .env file
load_dotenv()

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


@app.post("/api/chat/sync")
async def chat_sync(request: ChatRequest) -> ChatResponse:
    """Synchronous endpoint for single-turn chat requests with no streaming"""
    config = {}
    
    # Thread id from request exists
    if request.thread_id:
        config["configurable"] = {"thread_id": request.thread_id}
    
    try:
        # Run the agent asynchronously
        result = await root_agent.ainvoke(
            {"messages": [("user", request.message)]},
            config=config
        )
        
        # Get final response from the last message in thread
        last_message = result["messages"][-1]
        response_text = getattr(last_message, "text", "")
        
        return ChatResponse(
            response=response_text,
            thread_id=result.get("configurable", {}).get("thread_id")
        )
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))
