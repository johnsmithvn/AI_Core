"""
AI Core - Main Entry Point
"""
import uvicorn


def main():
    """Start the API server"""
    uvicorn.run(
        "app.api.chat:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
