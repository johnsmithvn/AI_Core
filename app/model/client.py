"""Model Client - Abstraction layer cho việc gọi LLM"""
from typing import List, Dict, Any, Optional, Literal
import httpx
from datetime import datetime


ProviderType = Literal["openai", "anthropic", "local", "mock"]


class ModelClient:
    """
    Client để gọi các LLM providers.
    Hỗ trợ: OpenAI, Anthropic, local models, hoặc mock.
    """
    
    def __init__(
        self,
        provider: ProviderType = "mock",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "gpt-4",
        timeout: int = 30
    ):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.timeout = timeout
        
        # For mock mode
        self._mock_responses = []
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate completion from model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        
        Returns:
            {
                "content": str,
                "model": str,
                "usage": dict,
                "finish_reason": str
            }
        """
        if self.provider == "mock":
            return self._mock_complete(messages, temperature)
        elif self.provider == "openai":
            return await self._openai_complete(messages, temperature, max_tokens)
        elif self.provider == "anthropic":
            return await self._anthropic_complete(messages, temperature, max_tokens)
        elif self.provider == "local":
            return await self._local_complete(messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _mock_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float
    ) -> Dict[str, Any]:
        """Mock completion for testing"""
        user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            ""
        )
        
        # Simple mock response
        response = f"[MOCK] Tôi hiểu bạn hỏi: '{user_msg[:50]}...'. Đây là câu trả lời giả."
        
        return {
            "content": response,
            "model": "mock-model",
            "usage": {
                "prompt_tokens": sum(len(m["content"]) // 4 for m in messages),
                "completion_tokens": len(response) // 4,
                "total_tokens": 0
            },
            "finish_reason": "stop"
        }
    
    async def _openai_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """OpenAI API completion"""
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        url = self.base_url or "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
        
        choice = data["choices"][0]
        
        return {
            "content": choice["message"]["content"],
            "model": data["model"],
            "usage": data["usage"],
            "finish_reason": choice["finish_reason"]
        }
    
    async def _anthropic_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Anthropic API completion"""
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        url = self.base_url or "https://api.anthropic.com/v1/messages"
        
        # Convert messages format
        system_msg = next(
            (m["content"] for m in messages if m["role"] == "system"),
            None
        )
        
        converted_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages if m["role"] != "system"
        ]
        
        payload = {
            "model": self.model_name,
            "messages": converted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 1024
        }
        
        if system_msg:
            payload["system"] = system_msg
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            data = response.json()
        
        return {
            "content": data["content"][0]["text"],
            "model": data["model"],
            "usage": data["usage"],
            "finish_reason": data["stop_reason"]
        }
    
    async def _local_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Local model completion (llama.cpp, vLLM, etc.)"""
        if not self.base_url:
            raise ValueError("Base URL required for local model")
        
        # Assume OpenAI-compatible API
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        
        choice = data["choices"][0]
        
        return {
            "content": choice["message"]["content"],
            "model": data.get("model", self.model_name),
            "usage": data.get("usage", {}),
            "finish_reason": choice.get("finish_reason", "stop")
        }
    
    def set_mock_response(self, response: str) -> None:
        """Set mock response for testing"""
        self._mock_responses.append(response)
