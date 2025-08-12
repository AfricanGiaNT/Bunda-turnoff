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
    import os
    import uvicorn
    
    # Get port from environment variable with validation
    port_str = os.environ.get('PORT', '8000')
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
        print(f"Invalid PORT value '{port_str}', using default port 8000")
    
    print(f"Environment PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"Using port: {port}")
    print(f"Starting standalone FastAPI server on 0.0.0.0:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
