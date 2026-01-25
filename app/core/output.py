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
            "max_length": 1000,
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
        
        # Check length
        max_length = self.rules.get("max_length", 1000)
        if len(content) > max_length:
            warnings.append(f"Output exceeds max length ({len(content)}/{max_length})")
            content = content[:max_length] + "..."
        
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
        
        # Clean up formatting
        content = self._cleanup_formatting(content)
        
        # Build metadata
        metadata = {
            "persona_used": persona.get("name"),
            "context_type": context.get("context_type"),
            "confidence": context.get("confidence"),
            "length": len(content)
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
