"""Output Processor - Xử lý và validate output từ model"""
from typing import Dict, Any, Optional
import re


class OutputProcessor:
    """
    Xử lý output từ model trước khi trả về user.
    - Validate theo rules
    - Clean up formatting
    - Add metadata
    """
    
    def __init__(self, rules: Optional[dict] = None):
        self.rules = rules or self._default_rules()
    
    @staticmethod
    def _default_rules() -> dict:
        """Default output rules"""
        return {
            "max_length": None,  # No limit for local AI
            "must_be_honest": True,
            "can_refuse": True,
            "can_joke_about_attitude": True,
            "cannot_joke_about_facts": True
        }
    
    def process(
        self,
        raw_output: str,
        context: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process model output.
        
        Args:
            raw_output: Raw text from model
            context: Context analysis
            persona: Persona config
        
        Returns:
            {
                "content": str,
                "valid": bool,
                "warnings": list[str],
                "metadata": dict
            }
        """
        content = raw_output.strip()
        warnings = []
        
        # Clean up formatting first
        content = self._cleanup_formatting(content)
        
        # LEVEL 2.3: Length awareness theo context (behavior validation, NOT truncate)
        warnings.extend(self._validate_length_behavior(content, context))
        
        # Check for dishonesty patterns (simple heuristic)
        if self.rules.get("must_be_honest"):
            dishonest_patterns = [
                r"tôi chắc chắn",
                r"100%",
                r"hoàn toàn đúng",
                r"không thể sai"
            ]
            
            for pattern in dishonest_patterns:
                if re.search(pattern, content.lower()):
                    warnings.append(f"Potentially overconfident language: {pattern}")
        
        # LEVEL 1.2: Build metadata - mô tả nội dung, không kiểm soát
        word_count = len(content.split())
        metadata = {
            "persona_used": persona.get("name"),
            "context_type": context.get("context_type"),
            "response_mode": context.get("response_mode"),  # NEW: how AI responded
            "confidence": context.get("confidence"),
            "length": len(content),
            "word_count": word_count,
            "estimated_read_time": max(1, word_count // 200),  # minutes
            "has_code_blocks": bool(re.search(r'```', content))
        }
        
        return {
            "content": content,
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "metadata": metadata
        }
    
    def _cleanup_formatting(self, text: str) -> str:
        """Clean up text formatting"""
        # Remove extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def _validate_length_behavior(self, content: str, context: Dict[str, Any]) -> list[str]:
        """LEVEL 2.3: Validate length behavior based on context (NOT truncate)"""
        warnings = []
        length = len(content)
        context_type = context.get("context_type", "unknown")
        confidence = context.get("confidence", 1.0)
        
        # Casual chat → dài bất thường = warning
        if context_type == "casual" and length > 3000:
            warnings.append("Casual response unusually long (>3000 chars)")
        
        # response_mode=cautious + dài + chắc chắn = suspicious
        response_mode = context.get("response_mode", context_type)
        if response_mode == "cautious" and length > 2000:
            # Check if response has certainty language
            has_certainty = any(
                phrase in content.lower() 
                for phrase in ["chắc chắn", "100%", "hoàn toàn đúng"]
            )
            if has_certainty:
                warnings.append("Cautious response_mode but long response with high certainty")
        
        # Low confidence + very long = suspicious
        if confidence < 0.5 and length > 2500:
            warnings.append(f"Low confidence ({confidence:.0%}) but very long response")
        
        return warnings
    
    def validate_honesty(self, output: str, context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate if output follows honesty rules.
        
        Returns:
            (is_honest: bool, reason: str)
        """
        output_lower = output.lower()
        
        # Check if claiming certainty without evidence
        certainty_phrases = [
            "chắc chắn 100%",
            "tôi biết chắc",
            "không thể sai"
        ]
        
        has_uncertainty = any(
            phrase in output_lower 
            for phrase in ["có thể", "không chắc", "tôi nghĩ", "hình như"]
        )
        
        has_certainty = any(
            phrase in output_lower 
            for phrase in certainty_phrases
        )
        
        # If low confidence but high certainty language → dishonest
        if context.get("confidence", 1.0) < 0.5 and has_certainty:
            return (False, "Claiming certainty with low context confidence")
        
        # If needs knowledge but doesn't have it, should admit
        if context.get("needs_knowledge") and not has_uncertainty:
            return (False, "Should express uncertainty when knowledge is needed")
        
        return (True, "")
