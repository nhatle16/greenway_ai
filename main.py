from fastapi import FastAPI


# Initialize the FastAPI application
app = FastAPI(
    title="Greenway AI Agent API",
    version="1.0.0"
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
