"""Memory Schema Definitions"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


class Message(BaseModel):
    """Single conversation message"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant", "system"]
    content: str
    persona: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Memory(BaseModel):
    """Memory entry for storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["short_term", "long_term", "knowledge"]
    content: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    source: Literal["user", "doc", "system"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolCall(BaseModel):
    """Tool execution record"""
    tool: str
    input: dict
    output: Optional[dict] = None
    status: Literal["success", "failed"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Session(BaseModel):
    """Conversation session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    messages: list[Message] = []
    context: dict = {}
