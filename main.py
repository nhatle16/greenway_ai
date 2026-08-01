from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


# Define a health check route
@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend server status."""
    return {
        "status": "ok",
        "service": "greenway_ai",
        "version": "1.0.0"
    }
