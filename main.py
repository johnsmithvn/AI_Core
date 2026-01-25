"""
AI Core - Main Entry Point
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Start the API server with dynamic configuration"""
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    
    print(f"🚀 Starting AI Core API Server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Auto-reload: {reload}")
    print(f"   Access at: http://localhost:{port}")
    print(f"   API Docs: http://localhost:{port}/docs")
    print("")
    
    uvicorn.run(
        "app.api.chat:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
