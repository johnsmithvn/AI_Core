"""Prompt Builder - Xây dựng prompt gửi tới model"""
from typing import List, Dict, Any, Optional
from app.memory.schema import Message


class PromptBuilder:
    """
    Xây dựng prompt cuối cùng gửi đến model.
    Bao gồm:
    - System prompt
    - Conversation history
    - Current user input
    - Persona instructions
    """
    
    BASE_SYSTEM_PROMPT = """
PHẦN I — KIẾN TRÚC Haruna (BẢN CHUẨN)
======================================
Bạn là Haruna được thiết kế như một người bạn trò chuyện thông minh.

BẢN CHẤT:
- Nói chuyện tự nhiên, có duyên, giống người thật
- Có thể đùa, cà khịa nhẹ, né câu hỏi
- Không giáo điều, không khoe kiến thức

NGUYÊN TẮC BẮT BUỘC:
- Được đùa về thái độ, KHÔNG đùa về sự thật
- Không chắc thì phải nói "tôi không chắc"
- Thiếu thông tin thì được từ chối có duyên và gạ thêm context
- Tuyệt đối không bịa kiến thức để làm vui

HÀNH VI:
- Tự nhận biết ngữ cảnh để đổi giọng:
  - chat chơi → thoải mái
  - hỏi nghiêm túc → đúng, rõ
- Câu nói hay / châm biếm / triết lý chỉ dùng khi phù hợp ngữ cảnh

QUẢN LÝ ĐỘ DÀI CÂU TRẢ LỜI:
- Nếu câu trả lời bắt đầu quá dài (>500 từ), được phép:
  + Tóm tắt phần quan trọng trước
  + Hỏi user "Bạn muốn tôi giải thích chi tiết hơn không?"
  + Chia thành nhiều phần nếu cần
- Đây là cách người thật nói chuyện, không ai muốn nghe monologue dài

KIẾN THỨC:
- Kiến thức nền đến từ model gốc
- Nội dung cụ thể (sách, truyện, câu hay, kinh nghiệm) đến từ trí nhớ ngoài
- Nếu không có dữ liệu phù hợp, phải thừa nhận
- Kiến thức được nạp thông qua input từ việc thu thập các mẩu truyện / các mẩu comment trên social để hình thành từ vựng và câu ngữ pháp vui vẻ, sắc sảo

MỤC TIÊU CUỐI:
- Tạo cảm giác đang nói chuyện với một người biết điều
- Thông minh nhưng khiêm tốn
- Hài hước nhưng trung thực
""".strip()
    
    def __init__(self):
        self.base_system = self.BASE_SYSTEM_PROMPT
    
    def build(
        self,
        user_input: str,
        history: List[Message],
        persona_config: Dict[str, Any],
        context: Dict[str, Any],
        knowledge: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build complete prompt for model.
        
        Args:
            user_input: Current user message
            history: Recent conversation history
            persona_config: Selected persona configuration
            context: Context analysis result
            knowledge: Retrieved knowledge if any
        
        Returns:
            List of messages in OpenAI format
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(
            persona_config,
            context,
            knowledge
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history (ensure alternating user/assistant pattern)
        # Filter to only include complete user-assistant pairs
        filtered_history = self._filter_history_for_alternating(history)
        for msg in filtered_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def _build_system_prompt(
        self,
        persona_config: Dict[str, Any],
        context: Dict[str, Any],
        knowledge: Optional[str] = None
    ) -> str:
        """Build system prompt with persona and context"""
        parts = [self.base_system]
        
        # Add persona instructions
        persona_additions = persona_config.get("system_prompt_additions", "")
        if persona_additions:
            parts.append(f"\n--- Persona hiện tại ---\n{persona_additions}")
        
        # Add context info
        if context.get("needs_knowledge") and not knowledge:
            parts.append(
                "\n⚠️ Lưu ý: User đang hỏi về kiến thức cụ thể nhưng không có dữ liệu. "
                "Hãy từ chối một cách có duyên và gợi ý cần thêm thông tin."
            )
        
        # Add retrieved knowledge
        if knowledge:
            parts.append(f"\n--- Kiến thức liên quan ---\n{knowledge}")
        
        # Add confidence warning
        confidence = context.get("confidence", 1.0)
        if confidence < 0.5:
            parts.append(
                f"\n⚠️ Độ tự tin về ngữ cảnh: {confidence:.0%} - Hãy thận trọng trong câu trả lời."
            )
        
        return "\n".join(parts)
    
    def _filter_history_for_alternating(self, history: List[Message]) -> List[Message]:
        """
        Filter history to ensure proper alternating user/assistant pattern.
        Rules:
        - Must start with 'user' role
        - Must alternate between user and assistant
        - Remove any messages that break the pattern
        """
        if not history:
            return []
        
        filtered = []
        expected_role = "user"  # Always start with user
        
        for msg in history:
            if msg.role == expected_role:
                filtered.append(msg)
                # Toggle expected role
                expected_role = "assistant" if expected_role == "user" else "user"
        
        # If history ends with assistant (which is expected), keep it
        # If it ends with user (incomplete pair), also keep it
        return filtered
    
    def build_simple(self, user_input: str) -> List[Dict[str, str]]:
        """Build simple prompt without context (for quick testing)"""
        return [
            {"role": "system", "content": self.base_system},
            {"role": "user", "content": user_input}
        ]
