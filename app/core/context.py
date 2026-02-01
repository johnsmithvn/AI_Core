"""Context Analyzer - Phân tích ngữ cảnh"""
from typing import Literal, Dict, Any
from app.memory.schema import Message
import yaml
from pathlib import Path


ContextType = Literal["casual", "technical", "cautious"]


class ContextAnalyzer:
    """
    Phân tích ngữ cảnh từ input của user.
    Quyết định user đang:
    - chat chơi
    - hỏi kỹ thuật
    - cần tìm kiến thức
    """
    
    def __init__(self, rules_path: str = "app/config/rules.yaml"):
        self.rules = self._load_rules(rules_path)
    
    def _load_rules(self, path: str) -> dict:
        """Load context detection rules"""
        rules_file = Path(path)
        if not rules_file.exists():
            return self._default_rules()
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def _default_rules() -> dict:
        """Default rules if config not found"""
        return {
            "context_detection": {
                "casual_chat": {
                    "keywords": ["chơi", "cười", "đùa", "haha", "lol"],
                    "confidence_threshold": 0.7
                },
                "technical_question": {
                    "keywords": ["code", "debug", "lỗi", "làm sao", "giải thích"],
                    "confidence_threshold": 0.6
                },
                "need_knowledge": {
                    "keywords": ["sách", "truyện", "tài liệu", "kinh nghiệm", "câu nói"],
                    "confidence_threshold": 0.5
                }
            }
        }
    
    def analyze(self, user_input: str, history: list[Message] = None) -> Dict[str, Any]:
        """
        Phân tích ngữ cảnh từ input.
        
        Returns:
            {
                "context_type": "casual" | "technical" | "cautious",
                "confidence": 0.0-1.0,
                "needs_knowledge": bool,
                "indicators": list[str]
            }
        """
        text_lower = user_input.lower()
        detection = self.rules.get("context_detection", {})
        
        # Check each context type
        casual_score = self._calculate_score(
            text_lower,
            detection.get("casual_chat", {})
        )
        
        technical_score = self._calculate_score(
            text_lower,
            detection.get("technical_question", {})
        )
        
        knowledge_score = self._calculate_score(
            text_lower,
            detection.get("need_knowledge", {})
        )
        
        # Determine context type (casual or technical - what user is asking)
        context_scores = {
            "casual": casual_score,
            "technical": technical_score
        }
        context_type = max(context_scores, key=context_scores.get)
        
        # Check if knowledge retrieval needed
        knowledge_threshold = detection.get("need_knowledge", {}).get("confidence_threshold", 0.5)
        needs_knowledge = knowledge_score > knowledge_threshold
        
        # Determine response_mode (how AI should respond)
        # - cautious: when needs_knowledge (thận trọng, không bịa)
        # - otherwise: follow context_type
        if needs_knowledge:
            response_mode = "cautious"
        else:
            response_mode = context_type
        
        # Signal strength = max of relevant scores
        # LƯU Ý: Đây KHÔNG phải xác suất đúng, chỉ là "mức độ có tín hiệu keyword"
        all_scores = {**context_scores, "knowledge": knowledge_score}
        signal_strength = max(all_scores.values())
        
        # Context clarity: Có rõ ràng không hay bị conflict?
        # True = chỉ 1 loại có signal, False = cả 2 đều có hoặc đều không
        has_casual_signal = casual_score > 0
        has_technical_signal = technical_score > 0
        context_clarity = (has_casual_signal != has_technical_signal)  # XOR
        
        # Collect indicators
        indicators = self._get_indicators(text_lower, detection)
        
        return {
            "context_type": context_type,      # casual | technical (what user is asking)
            "response_mode": response_mode,    # casual | technical | cautious (how AI responds)
            "signal_strength": signal_strength,  # Mức độ tín hiệu keyword (KHÔNG phải xác suất)
            "context_clarity": context_clarity,  # True = rõ ràng, False = có conflict/mơ hồ
            "needs_knowledge": needs_knowledge,
            "indicators": indicators,
            "scores": all_scores,
            # Legacy support
            "confidence": signal_strength  # Deprecated, use signal_strength
        }
    
    def _calculate_score(self, text: str, config: dict) -> float:
        """
        Calculate matching score for a context type.
        
        Logic: Nếu có BẤT KỲ keyword nào match → score = 1.0 / (1 + penalty)
        - Nhiều keywords match → score cao hơn
        - Ít nhất 1 match → score > threshold (0.1)
        
        Cũ: matches / total_keywords → list dài = score thấp (sai logic)
        Mới: Có match = có signal, số match tăng = confidence tăng
        """
        keywords = config.get("keywords", [])
        if not keywords:
            return 0.0
        
        matches = sum(1 for kw in keywords if kw in text)
        
        if matches == 0:
            return 0.0
        
        # 1 match = 0.5, 2 matches = 0.67, 3 matches = 0.75, ...
        # Formula: matches / (matches + 1)
        # Đảm bảo: 1 match luôn > 0.1 threshold
        return matches / (matches + 1)
    
    def _get_indicators(self, text: str, detection: dict) -> list[str]:
        """Get matched keyword indicators"""
        indicators = []
        
        for context_name, config in detection.items():
            keywords = config.get("keywords", [])
            matched = [kw for kw in keywords if kw in text]
            indicators.extend(matched)
        
        return indicators
    
    def should_refuse(self, user_input: str, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Quyết định có nên từ chối trả lời không.
        
        Returns:
            (should_refuse: bool, reason: str)
        """
        # Nếu câu hỏi quá ngắn (< 5 chars)
        if len(user_input.strip()) < 5:
            return (True, "Câu hỏi hơi ngắn, bạn hỏi cụ thể hơn được không?")
        
        # NOTE: Không refuse chỉ vì needs_knowledge + low confidence
        # Low confidence là do thuật toán score, không phải câu hỏi mơ hồ
        # AI sẽ tự xử lý qua behavior "cautious" - thừa nhận không biết
        
        return (False, "")
