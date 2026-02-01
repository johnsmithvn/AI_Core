"""AI Core Engine - Thành phần trung tâm điều phối mọi thứ"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.context import ContextAnalyzer
from app.core.persona import PersonaSelector
from app.core.prompt import PromptBuilder
from app.core.output import OutputProcessor
from app.core.logging import get_logger
from app.memory import ShortTermMemory, LongTermMemory, Message
from app.model import ModelClient

logger = get_logger(__name__)


class AICore:
    """
    AI Core Engine - não của hệ thống.
    
    Luồng xử lý:
    1. Nhận input từ user
    2. Phân tích ngữ cảnh (ContextAnalyzer)
    3. Chọn persona phù hợp (PersonaSelector)
    4. Load memory (ShortTermMemory + LongTermMemory)
    5. Build prompt (PromptBuilder)
    6. Gọi model (ModelClient)
    7. Xử lý output (OutputProcessor)
    8. Lưu vào memory
    9. Trả về response
    """
    
    def __init__(
        self,
        model_client: ModelClient,
        context_analyzer: Optional[ContextAnalyzer] = None,
        persona_selector: Optional[PersonaSelector] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        output_processor: Optional[OutputProcessor] = None,
        short_term_memory: Optional[ShortTermMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None
    ):
        # Core components
        self.model = model_client
        self.context_analyzer = context_analyzer or ContextAnalyzer()
        self.persona_selector = persona_selector or PersonaSelector()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.output_processor = output_processor or OutputProcessor()
        
        # Memory
        self.short_memory = short_term_memory or ShortTermMemory()
        self.long_memory = long_term_memory or LongTermMemory()
    
    async def process(
        self,
        user_input: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main processing pipeline.
        
        Args:
            user_input: User's message
            session_id: Session ID for context
        
        Returns:
            {
                "response": str,
                "metadata": dict,
                "session_id": str
            }
        """
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "process_start",
            request_id=request_id,
            session_id=session_id,
            input_length=len(user_input)
        )
        
        # 1. Get or create session
        session = self.short_memory.get_session(session_id)
        if not session:
            session = self.short_memory.create_session(session_id)
            logger.info("session_created", request_id=request_id, session_id=session.id)
        
        # 2. Get conversation history
        history = self.short_memory.get_recent_messages(session.id, limit=10)
        
        # 3. Analyze context
        context = self.context_analyzer.analyze(user_input, history)
        logger.debug(
            "context_analyzed",
            request_id=request_id,
            context_type=context["context_type"],
            confidence=context["confidence"]
        )
        
        # 4. Check if should refuse
        should_refuse, refuse_reason = self.context_analyzer.should_refuse(
            user_input,
            context
        )
        
        if should_refuse:
            logger.info(
                "request_refused",
                request_id=request_id,
                reason=refuse_reason
            )
            # Return polite refusal
            response_msg = Message(
                role="assistant",
                content=refuse_reason,
                persona="cautious"
            )
            self.short_memory.add_message(session.id, response_msg)
            
            return {
                "response": refuse_reason,
                "metadata": {
                    "refused": True,
                    "reason": refuse_reason,
                    "context": context
                },
                "session_id": session.id
            }
        
        # 5. Select persona
        persona = self.persona_selector.select(context)
        logger.debug(
            "persona_selected",
            request_id=request_id,
            persona=persona["name"],
            temperature=persona["temperature"]
        )
        
        # 6. Retrieve knowledge if needed
        knowledge = None
        if context.get("needs_knowledge"):
            logger.debug("retrieving_knowledge", request_id=request_id)
            knowledge = self._retrieve_knowledge(user_input)
            if knowledge:
                logger.info("knowledge_retrieved", request_id=request_id, length=len(knowledge))
        
        # 7. Build prompt
        messages = self.prompt_builder.build(
            user_input=user_input,
            history=history,
            persona_config=persona,
            context=context,
            knowledge=knowledge
        )
        
        # 8. Call model
        logger.info(
            "calling_model",
            request_id=request_id,
            provider=self.model.provider,
            model=self.model.model_name
        )
        
        model_response = await self.model.complete(
            messages=messages,
            temperature=persona.get("temperature", 0.7)
        )
        
        raw_output = model_response["content"]
        logger.info(
            "model_response_received",
            request_id=request_id,
            response_length=len(raw_output),
            usage=model_response.get("usage", {})
        )
        
        # 9. Process output
        processed = self.output_processor.process(
            raw_output=raw_output,
            context=context,
            persona=persona
        )
        
        # 10. Validate honesty
        is_honest, honesty_issue = self.output_processor.validate_honesty(
            processed["content"],
            context
        )
        
        if not is_honest:
            processed["warnings"].append(f"Honesty issue: {honesty_issue}")
            logger.warning(
                "honesty_issue",
                request_id=request_id,
                issue=honesty_issue
            )
        
        # 11. Save to memory
        user_msg = Message(
            role="user",
            content=user_input,
            persona=None  # User messages don't have persona
        )
        self.short_memory.add_message(session.id, user_msg)
        
        assistant_msg = Message(
            role="assistant",
            content=processed["content"],
            persona=persona["name"]
        )
        self.short_memory.add_message(session.id, assistant_msg)
        
        # 12. Return response
        logger.info(
            "process_complete",
            request_id=request_id,
            session_id=session.id,
            persona=persona["name"],
            valid=processed["valid"],
            warnings_count=len(processed["warnings"])
        )
        
        return {
            "response": processed["content"],
            "metadata": {
                "persona": persona["name"],
                "context": context,
                "valid": processed["valid"],
                "warnings": processed["warnings"],
                "model_info": {
                    "model": model_response["model"],
                    "usage": model_response["usage"]
                }
            },
            "session_id": session.id
        }
    
    def _retrieve_knowledge(self, query: str) -> Optional[str]:
        """
        Retrieve relevant knowledge from long-term memory.
        
        TODO: Implement proper RAG with vector search.
        For now, just search by keyword.
        """
        memories = self.long_memory.search(
            memory_type="knowledge",
            min_confidence=0.5,
            limit=3
        )
        
        if not memories:
            return None
        
        # Combine memories
        knowledge_parts = [m.content for m in memories]
        return "\n\n".join(knowledge_parts)
    
    def cleanup(self) -> None:
        """Cleanup old sessions and memories"""
        logger.info("cleanup_start")
        
        # Cleanup old sessions (older than 1 hour)
        removed_sessions = self.short_memory.cleanup_old_sessions(max_age_seconds=3600)
        
        # Cleanup old memories (older than 30 days)
        removed_memories = self.long_memory.cleanup_old(days=30)
        
        logger.info(
            "cleanup_complete",
            removed_sessions=removed_sessions,
            removed_memories=removed_memories
        )
        
        return {
            "removed_sessions": removed_sessions,
            "removed_memories": removed_memories
        }
