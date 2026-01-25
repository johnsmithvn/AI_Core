"""Long-term memory with SQLite persistence"""
from typing import List, Optional
from datetime import datetime
import sqlite3
import json
from pathlib import Path
from app.memory.schema import Memory


class LongTermMemory:
    """
    Persistent memory storage using SQLite.
    Stores important facts, knowledge, and user preferences.
    """
    
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_type 
            ON memories(type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON memories(created_at DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def save(self, memory: Memory) -> None:
        """Save memory to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(memory.metadata) if memory.metadata else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, type, content, confidence, source, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.type,
            memory.content,
            memory.confidence,
            memory.source,
            memory.created_at.isoformat(),
            metadata_json
        ))
        
        conn.commit()
        conn.close()
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Retrieve memory by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, type, content, confidence, source, created_at, metadata
            FROM memories WHERE id = ?
        """, (memory_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_memory(row)
    
    def search(
        self,
        memory_type: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 10
    ) -> List[Memory]:
        """Search memories by filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, type, content, confidence, source, created_at, metadata
            FROM memories WHERE confidence >= ?
        """
        params = [min_confidence]
        
        if memory_type:
            query += " AND type = ?"
            params.append(memory_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def delete(self, memory_id: str) -> bool:
        """Delete memory by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def cleanup_old(self, days: int = 30) -> int:
        """Remove memories older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        cursor.execute("""
            DELETE FROM memories WHERE created_at < ?
        """, (cutoff_iso,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    @staticmethod
    def _row_to_memory(row: tuple) -> Memory:
        """Convert database row to Memory object"""
        metadata = json.loads(row[6]) if row[6] else None
        
        return Memory(
            id=row[0],
            type=row[1],
            content=row[2],
            confidence=row[3],
            source=row[4],
            created_at=datetime.fromisoformat(row[5]),
            metadata=metadata
        )
