"""
Standalone FastAPI application with no external dependencies.
This is to test if the issue is with module imports.
"""

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="Service Station Operations Bot",
    description="Standalone test version",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Standalone Service Station Operations Bot API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Standalone bot is running"
    }

@app.get("/test")
async def test():
    """Test endpoint."""
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
