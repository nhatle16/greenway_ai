import asyncio
import json
import logging
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

from src.agent import root_agent

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# `langgraph dev` supplies its own persistence, so only the FastAPI copy gets one
# shortcut: in-memory, so threads and facts are lost on restart; use a SQLite/Postgres saver and store to keep them
agent = root_agent.copy(update={"checkpointer": InMemorySaver(), "store": InMemoryStore()})

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
    # shortcut: the client picks its own id with no login, so it only separates users, it doesn't authenticate them; derive it from auth once there is any
    user_id: str = Field(default="default_user", min_length=1, max_length=64, description="Whose long-term facts to read and save")

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
    # A checkpointer needs a thread id, so start a new thread when none is given
    thread_id = request.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Run the agent asynchronously
        result = await agent.ainvoke(
            {"messages": [("user", request.message)]},
            config=config,
            context={"user_id": request.user_id},
        )
    except Exception:
        logger.exception("Agent sync call failed")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.") from None

    # Get final response from the last message in thread
    last_message = result["messages"][-1]
    response_text = getattr(last_message, "text", "")

    return ChatResponse(response=response_text, thread_id=thread_id)

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming endpoint yielding Server-Sent Events (SSE) token-by-token."""
    # A checkpointer needs a thread id, so start a new thread when none is given
    thread_id = request.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    async def event_generator():
        try:
            # Send initial metadata chunk with the active thread_id
            init_payload = json.dumps({"type": "meta", "thread_id": thread_id})
            yield f"data: {init_payload}\n\n"
            
            async for event in agent.astream_events(
                {"messages": [("user", request.message)]},
                config=config,
                context={"user_id": request.user_id},
                version="v2"
            ):
                kind = event.get("event")
                
                # Stream raw LLM text tokens
                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")  # extract message chunk
                    if chunk and hasattr(chunk, "content"):     # extract content
                        content = chunk.content
                        text_content = ""
                        if isinstance(content, str):            # content is a plain string
                            text_content = content
                        elif isinstance(content, list):         # content is a list of 
                            parts = []
                            for block in content:
                                if isinstance(block, str):      # the item is a plain string
                                    parts.append(block)
                                # the item is a block dict
                                elif isinstance(block, dict) and block.get("type") == "text":
                                    parts.append(block.get("text", ""))
                                elif isinstance(block, dict) and "text" in block:
                                    parts.append(str(block["text"]))
                            text_content = "".join(parts)       # combining text blocks into a single string

                        if text_content:
                            payload = json.dumps({"type": "stream", "content": text_content})
                            yield f"data: {payload}\n\n"
                            await asyncio.sleep(0)  # flush control back to event loop
                
                # Stream tool execution
                elif kind == "on_tool_start":
                    tool_input = event.get("data", {}).get("input")
                    payload = json.dumps({
                        "type": "tool_start",
                        "tool": event.get("name"),
                        "input": str(tool_input) if tool_input is not None else None
                    })
                    yield f"data: {payload}\n\n"
                    
                elif kind == "on_tool_end":
                    tool_output = event.get("data", {}).get("output")
                    output_str = getattr(tool_output, "content", str(tool_output)) if tool_output is not None else None
                    payload = json.dumps({
                        "type": "tool_end",
                        "tool": event.get("name"),
                        "output": output_str
                    })
                    yield f"data: {payload}\n\n"
                    
            done_payload = json.dumps({"type": "done", "thread_id": thread_id})
            yield f"data: {done_payload}\n\n"
                
        except Exception:  # noqa: BLE001
            # Full details stay in server logs; the client gets a generic message
            logger.exception("Agent stream failed")
            error_payload = json.dumps({"type": "error", "detail": "Something went wrong. Please try again."})
            yield f"data: {error_payload}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")
