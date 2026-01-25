"""Short-term memory management (in-session)"""
from typing import List, Optional
from datetime import datetime
from app.memory.schema import Message, Session


class ShortTermMemory:
    """
    Manages conversation context within a session.
    Keeps recent messages in memory for quick access.
    """
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.sessions: dict[str, Session] = {}
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get existing session or None"""
        return self.sessions.get(session_id)
    
    def create_session(self, session_id: Optional[str] = None) -> Session:
        """Create new session"""
        session = Session(id=session_id) if session_id else Session()
        self.sessions[session.id] = session
        return session
    
    def add_message(self, session_id: str, message: Message) -> None:
        """Add message to session"""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        session.messages.append(message)
        session.last_activity = datetime.utcnow()
        
        # Trim old messages
        if len(session.messages) > self.max_messages:
            session.messages = session.messages[-self.max_messages:]
    
    def get_recent_messages(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get recent messages from session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context(self, session_id: str) -> dict:
        """Get session context metadata"""
        session = self.get_session(session_id)
        if not session:
            return {}
        return session.context
    
    def update_context(self, session_id: str, context: dict) -> None:
        """Update session context"""
        session = self.get_session(session_id)
        if session:
            session.context.update(context)
            session.last_activity = datetime.utcnow()
    
    def clear_session(self, session_id: str) -> None:
        """Clear session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_old_sessions(self, max_age_seconds: int = 3600) -> int:
        """Remove sessions older than max_age_seconds"""
        now = datetime.utcnow()
        to_remove = []
        
        for session_id, session in self.sessions.items():
            age = (now - session.last_activity).total_seconds()
            if age > max_age_seconds:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return len(to_remove)
