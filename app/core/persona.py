"""Persona Selector - Chọn tính cách phù hợp"""
from typing import Dict, Any
import yaml
from pathlib import Path


class PersonaSelector:
    """
    Chọn persona phù hợp dựa trên context đã phân tích.
    Persona quyết định:
    - Giọng điệu
    - Độ hài hước
    - Temperature khi gọi model
    """
    
    def __init__(self, persona_path: str = "app/config/persona.yaml"):
        self.personas = self._load_personas(persona_path)
        self.default_persona = self.personas.get(
            self.personas.get("default", "casual"), 
            {}
        )
    
    def _load_personas(self, path: str) -> dict:
        """Load persona configurations"""
        persona_file = Path(path)
        if not persona_file.exists():
            return self._default_personas()
        
        with open(persona_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get("personas", {})
    
    @staticmethod
    def _default_personas() -> dict:
        """Default personas if config not found"""
        return {
            "default": "casual",
            "casual": {
                "name": "Casual",
                "temperature": 0.8,
                "tone": ["thân thiện", "hài hước"],
                "patterns": ["đùa nhẹ", "né câu hỏi có duyên"]
            },
            "technical": {
                "name": "Technical",
                "temperature": 0.3,
                "tone": ["rõ ràng", "chính xác"],
                "patterns": ["trả lời đầy đủ", "ví dụ cụ thể"]
            },
            "cautious": {
                "name": "Cautious",
                "temperature": 0.5,
                "tone": ["thận trọng", "trung thực"],
                "patterns": ["nói rõ độ tự tin", "không bịa"]
            }
        }
    
    def select(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chọn persona dựa trên context.
        
        Args:
            context: Output từ ContextAnalyzer
        
        Returns:
            {
                "name": str,
                "temperature": float,
                "tone": list,
                "patterns": list,
                "system_prompt_additions": str
            }
        """
        context_type = context.get("context_type", "casual")
        confidence = context.get("confidence", 0.5)
        
        # Select persona
        persona = self.personas.get(context_type, self.default_persona)
        
        # Build system prompt additions
        tone_desc = ", ".join(persona.get("tone", []))
        patterns_desc = "; ".join(persona.get("patterns", []))
        
        system_additions = f"""
Giọng điệu: {tone_desc}
Hành vi: {patterns_desc}
Độ tự tin context: {confidence:.2f}
"""
        
        return {
            "name": persona.get("name", "Unknown"),
            "temperature": persona.get("temperature", 0.7),
            "tone": persona.get("tone", []),
            "patterns": persona.get("patterns", []),
            "system_prompt_additions": system_additions.strip()
        }
    
    def get_persona(self, name: str) -> Dict[str, Any]:
        """Get specific persona by name"""
        return self.personas.get(name, self.default_persona)
    
    def list_personas(self) -> list[str]:
        """List available persona names"""
        return [k for k in self.personas.keys() if k != "default"]
