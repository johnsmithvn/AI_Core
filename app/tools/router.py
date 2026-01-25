"""Tool Router - Manages and routes tool calls"""
from typing import Dict, List, Optional, Any
from app.tools.base import BaseTool, ToolInput, ToolOutput


class ToolRouter:
    """
    Manages available tools and routes calls to them.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List available tool names"""
        return list(self.tools.keys())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Get schemas for all tools.
        Used to inform model about available functions.
        """
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute(self, tool_name: str, input_data: ToolInput) -> ToolOutput:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of tool to execute
            input_data: Input for the tool
        
        Returns:
            ToolOutput with results or error
        """
        tool = self.get_tool(tool_name)
        
        if not tool:
            return ToolOutput(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        try:
            return await tool.execute(input_data)
        except Exception as e:
            return ToolOutput(
                success=False,
                data=None,
                error=f"Tool execution error: {str(e)}"
            )
    
    async def execute_multiple(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[ToolOutput]:
        """
        Execute multiple tool calls.
        
        Args:
            tool_calls: List of {name: str, input: dict}
        
        Returns:
            List of ToolOutput results
        """
        results = []
        
        for call in tool_calls:
            tool_name = call.get("name")
            tool_input = call.get("input", {})
            
            result = await self.execute(tool_name, ToolInput(**tool_input))
            results.append(result)
        
        return results
