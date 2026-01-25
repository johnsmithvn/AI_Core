"""Base Tool Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ToolInput(BaseModel):
    """Base input schema for tools"""
    pass


class ToolOutput(BaseModel):
    """Base output schema for tools"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class BaseTool(ABC):
    """
    Base class for all tools.
    Tools extend AI capabilities with external functions.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        Execute the tool.
        
        Args:
            input_data: Tool-specific input
        
        Returns:
            ToolOutput with results
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for model to understand.
        
        Returns:
            OpenAI function calling format
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }


class SearchTool(BaseTool):
    """Example: Search tool"""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Search for information in knowledge base"
        )
    
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """Execute search"""
        # TODO: Implement actual search
        return ToolOutput(
            success=True,
            data={"results": []},
            error=None
        )


class CalculatorTool(BaseTool):
    """Example: Calculator tool"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations"
        )
    
    async def execute(self, input_data: ToolInput) -> ToolOutput:
        """Execute calculation"""
        # TODO: Implement actual calculator
        return ToolOutput(
            success=True,
            data={"result": 0},
            error=None
        )
