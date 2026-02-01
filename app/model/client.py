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
        """
        OpenAI API completion using Chat Completions endpoint.
        Docs: https://platform.openai.com/docs/api-reference/chat/create
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        # OpenAI Chat Completions endpoint
        url = self.base_url or "https://api.openai.com/v1/chat/completions"
        
        # Build request payload according to OpenAI API spec
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": False  # Explicitly disable streaming
        }
        
        # Optional parameters
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Headers according to OpenAI docs
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            # Parse response according to OpenAI format
            if not data.get("choices") or len(data["choices"]) == 0:
                raise ValueError("No choices returned from OpenAI API")
            
            choice = data["choices"][0]
            message = choice.get("message", {})
            
            if not message.get("content"):
                raise ValueError("No content in OpenAI response")
            
            return {
                "content": message["content"],
                "model": data.get("model", self.model_name),
                "usage": data.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }),
                "finish_reason": choice.get("finish_reason", "stop")
            }
            
        except httpx.HTTPStatusError as e:
            # Parse OpenAI error response
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", str(e))
            except:
                error_msg = str(e)
            raise ValueError(f"OpenAI API error: {error_msg}")
        
        except httpx.TimeoutException:
            raise ValueError(f"OpenAI API timeout after {self.timeout}s")
        
        except Exception as e:
            raise ValueError(f"OpenAI API request failed: {str(e)}")
    
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
        """
        Local model completion using OpenAI-compatible API.
        Supports: LM Studio, Ollama, vLLM, llama.cpp server
        Endpoint: /v1/chat/completions
        """
        if not self.base_url:
            raise ValueError("Base URL required for local model")
        
        # Get model name - either from config or auto-detect from server
        model_to_use = self.model_name
        if not model_to_use or model_to_use == "auto":
            model_to_use = await self._get_first_available_model()
        
        # Convert messages for models that don't support system role
        # (e.g., Mistral template only supports user/assistant)
        converted_messages = self._convert_messages_for_local(messages)
        
        # Build OpenAI-compatible request payload
        payload = {
            "model": model_to_use,  # Required when multiple models loaded
            "messages": converted_messages,
            "temperature": temperature,
            "stream": False  # Explicitly disable streaming
        }
        
        # Optional parameters
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Headers for OpenAI-compatible API
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use longer timeout for local models (may be slower)
        timeout = max(self.timeout, 60.0)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse OpenAI-compatible response
            if not data.get("choices") or len(data["choices"]) == 0:
                raise ValueError("No choices returned from local model API")
            
            choice = data["choices"][0]
            message = choice.get("message", {})
            
            if not message.get("content"):
                raise ValueError("No content in local model response")
            
            return {
                "content": message["content"],
                "model": data.get("model", "local-model"),  # Get actual model from response
                "usage": data.get("usage", {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }),
                "finish_reason": choice.get("finish_reason", "stop")
            }
            
        except httpx.HTTPStatusError as e:
            # Parse error response
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", {}).get("message", str(e))
            except:
                error_msg = str(e)
            raise ValueError(f"Local model API error: {error_msg}")
        
        except httpx.TimeoutException:
            raise ValueError(f"Local model timeout after {timeout}s - model may not be loaded")
        
        except httpx.ConnectError:
            raise ValueError(f"Cannot connect to {self.base_url} - is the server running?")
        
        except Exception as e:
            raise ValueError(f"Local model request failed: {str(e)}")
    
    async def _get_first_available_model(self) -> str:
        """
        Get first available model from local server.
        Uses /v1/models endpoint (OpenAI-compatible).
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                response.raise_for_status()
                data = response.json()
            
            models = data.get("data", [])
            if not models:
                raise ValueError("No models available on server")
            
            # Return first model's ID
            first_model = models[0].get("id", "unknown")
            return first_model
            
        except Exception as e:
            # Fallback if can't get models list
            raise ValueError(f"Cannot auto-detect model: {str(e)}. Please set LOCAL_MODEL_NAME in .env")
    
    def _convert_messages_for_local(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Convert messages for local models that don't support system role.
        Some models (e.g., Mistral) only support user/assistant roles.
        
        Strategy: Merge system message into first user message.
        """
        converted = []
        system_content = None
        
        for msg in messages:
            if msg["role"] == "system":
                # Collect system message content
                system_content = msg["content"]
            elif msg["role"] == "user":
                # If we have system content, prepend to first user message
                if system_content:
                    converted.append({
                        "role": "user",
                        "content": f"[System Instructions]\n{system_content}\n\n[User Message]\n{msg['content']}"
                    })
                    system_content = None  # Only prepend once
                else:
                    converted.append(msg)
            else:
                # assistant or other roles - pass through
                converted.append(msg)
        
        # If only system message (no user message yet), convert to user
        if system_content and not converted:
            converted.append({
                "role": "user",
                "content": f"[System Instructions]\n{system_content}"
            })
        
        return converted
    
    def set_mock_response(self, response: str) -> None:
        """Set mock response for testing"""
        self._mock_responses.append(response)
