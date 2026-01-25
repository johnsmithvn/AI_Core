"""FastAPI Chat Endpoint"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid

from app.core import AICore
from app.core.logging import setup_logging, get_logger
from app.model import ModelClient
import os
from dotenv import load_dotenv

load_dotenv()




# Setup logging
setup_logging(log_level="INFO", log_file="data/app.log")
logger = get_logger(__name__)


# Pydantic models for API
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    metadata: Dict[str, Any]


# Initialize FastAPI app
app = FastAPI(
    title="AI Core API",
    description="Conversational AI with personality and context awareness",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Core with provider selection
# Set MODEL_PROVIDER in .env: mock, openai, anthropic, or local
provider = os.getenv("MODEL_PROVIDER", "mock").lower()

if provider == "openai":
    model_client = ModelClient(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("OPENAI_MODEL", "gpt-4")
    )
elif provider == "anthropic":
    model_client = ModelClient(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    )
elif provider == "local":
    model_client = ModelClient(
        provider="local",
        base_url=os.getenv("LOCAL_MODEL_URL", "http://localhost:8080"),
        model_name=os.getenv("LOCAL_MODEL_NAME", "llama-3-8b")
    )
else:  # mock (default)
    model_client = ModelClient(provider="mock")
    
logger.info(f"AI Core initialized with provider: {provider}")
ai_core = AICore(model_client=model_client)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AI Core API",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Args:
        request: ChatRequest with message and optional session_id
    
    Returns:
        ChatResponse with AI response and metadata
    """
    logger.info(
        "chat_request",
        session_id=request.session_id,
        message_length=len(request.message)
    )
    
    try:
        # Process through AI Core
        result = await ai_core.process(
            user_input=request.message,
            session_id=request.session_id
        )
        
        logger.info(
            "chat_success",
            session_id=result["session_id"]
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            metadata=result["metadata"]
        )
    
    except Exception as e:
        logger.error(
            "chat_error",
            session_id=request.session_id,
            error=str(e),
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )


@app.post("/chat/new-session")
async def new_session():
    """
    Create a new chat session.
    
    Returns:
        New session ID
    """
    session_id = str(uuid.uuid4())
    ai_core.short_memory.create_session(session_id)
    
    return {
        "session_id": session_id,
        "created": True
    }


@app.get("/chat/history/{session_id}")
async def get_history(session_id: str, limit: int = 20):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Session ID
        limit: Max messages to return
    
    Returns:
        List of messages
    """
    messages = ai_core.short_memory.get_recent_messages(session_id, limit)
    
    if not messages:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "persona": msg.persona,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }


@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a chat session.
    
    Args:
        session_id: Session ID to clear
    
    Returns:
        Success status
    """
    ai_core.short_memory.clear_session(session_id)
    
    return {
        "session_id": session_id,
        "cleared": True
    }


@app.post("/admin/cleanup")
async def cleanup():
    """
    Admin endpoint to cleanup old sessions and memories.
    
    Returns:
        Cleanup statistics
    """
    result = ai_core.cleanup()
    
    return {
        "success": True,
        "removed_sessions": result["removed_sessions"],
        "removed_memories": result["removed_memories"]
    }


@app.get("/admin/stats")
async def stats():
    """
    Get system statistics.
    
    Returns:
        Current system stats
    """
    return {
        "active_sessions": len(ai_core.short_memory.sessions),
        "personas": ai_core.persona_selector.list_personas(),
        "model_provider": ai_core.model.provider
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
