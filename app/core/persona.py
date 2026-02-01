"""Persona Selector - Kết hợp Tone + Behavior"""
from typing import Dict, Any
import yaml
from pathlib import Path


class PersonaSelector:
    """
    Chọn persona dựa trên context đã phân tích.
    
    v2.0: Tách Tone và Behavior
    - Tone (giọng điệu): casual / technical - quyết định bởi context_type
    - Behavior (hành vi): normal / cautious - quyết định bởi needs_knowledge
    
    Kết hợp: tone + behavior = persona linh hoạt
    Ví dụ: casual tone + cautious behavior = "Vui vẻ nhưng không bịa"
    """
    
    def __init__(self, persona_path: str = "app/config/persona.yaml"):
        self.config = self._load_config(persona_path)
        self.tones = self.config.get("tones", {})
        self.behaviors = self.config.get("behaviors", {})
        self.defaults = self.config.get("defaults", {"tone": "casual", "behavior": "normal"})
        
        # Legacy support
        self.personas = self.config.get("personas", {})
    
    def _load_config(self, path: str) -> dict:
        """Load persona configurations"""
        persona_file = Path(path)
        if not persona_file.exists():
            return self._default_config()
        
        with open(persona_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def _default_config() -> dict:
        """Default config if file not found"""
        return {
            "tones": {
                "casual": {
                    "name": "Casual",
                    "temperature": 0.8,
                    "style": ["thân thiện", "hài hước"],
                    "prompt_hint": "Trả lời thân thiện, có thể đùa nhẹ."
                },
                "technical": {
                    "name": "Technical",
                    "temperature": 0.3,
                    "style": ["rõ ràng", "chính xác"],
                    "prompt_hint": "Trả lời rõ ràng, chính xác, có cấu trúc."
                }
            },
            "behaviors": {
                "normal": {
                    "name": "Normal",
                    "prompt_hint": "Trả lời tự nhiên theo hiểu biết của mình."
                },
                "cautious": {
                    "name": "Cautious",
                    "prompt_hint": "Nếu không chắc chắn, thừa nhận ngay. Không bịa."
                }
            },
            "defaults": {"tone": "casual", "behavior": "normal"}
        }
    
    def select(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chọn persona dựa trên context (v2.0 - tone + behavior).
        
        Args:
            context: Output từ ContextAnalyzer
                - context_type: casual | technical
                - needs_knowledge: bool
        
        Returns:
            {
                "name": str,           # Combined name: "Casual + Cautious"
                "tone": str,           # casual | technical
                "behavior": str,       # normal | cautious
                "temperature": float,
                "system_prompt_additions": str
            }
        """
        # Determine tone from context_type
        context_type = context.get("context_type", self.defaults["tone"])
        tone_config = self.tones.get(context_type, self.tones.get(self.defaults["tone"], {}))
        
        # Determine behavior from needs_knowledge
        needs_knowledge = context.get("needs_knowledge", False)
        behavior_key = "cautious" if needs_knowledge else "normal"
        behavior_config = self.behaviors.get(behavior_key, self.behaviors.get("normal", {}))
        
        # Get confidence for prompt
        confidence = context.get("confidence", 0.5)
        
        # Build combined system prompt
        tone_hint = tone_config.get("prompt_hint", "")
        behavior_hint = behavior_config.get("prompt_hint", "")
        
        system_additions = f"""
[Giọng điệu - {tone_config.get('name', 'Unknown')}]
{tone_hint}

[Hành vi - {behavior_config.get('name', 'Unknown')}]
{behavior_hint}
""".strip()
        
        # Combined name
        combined_name = f"{tone_config.get('name', 'Unknown')} + {behavior_config.get('name', 'Unknown')}"
        
        return {
            "name": combined_name,
            "tone": context_type,
            "behavior": behavior_key,
            "temperature": tone_config.get("temperature", 0.7),
            "tone_config": tone_config,
            "behavior_config": behavior_config,
            "system_prompt_additions": system_additions
        }
    
    def get_tone(self, name: str) -> Dict[str, Any]:
        """Get specific tone by name"""
        return self.tones.get(name, self.tones.get(self.defaults["tone"], {}))
    
    def get_behavior(self, name: str) -> Dict[str, Any]:
        """Get specific behavior by name"""
        return self.behaviors.get(name, self.behaviors.get("normal", {}))
    
    # Legacy support
    def get_persona(self, name: str) -> Dict[str, Any]:
        """Get specific persona by name (legacy)"""
        return self.personas.get(name, {})
    
    def list_tones(self) -> list[str]:
        """List available tone names"""
        return list(self.tones.keys())
    
    def list_behaviors(self) -> list[str]:
        """List available behavior names"""
        return list(self.behaviors.keys())
        return [k for k in self.personas.keys() if k != "default"]
