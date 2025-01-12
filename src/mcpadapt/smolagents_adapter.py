"""This module implements the SmolAgents adapter.

SmolAgents do not support async tools, so this adapter will only work with the sync
context manager.

Example Usage:
>>> with MCPAdapt(StdioServerParameters(command="uv", args=["run", "src/echo.py"]), SmolAgentAdapter()) as tools:
>>>     print(tools)
"""

from typing import Callable

import jsonref
import mcp
import smolagents

from mcpadapt.core import ToolAdapter


def snake_to_camel(s: str) -> str:
    return "".join(word.capitalize() for word in s.split("_"))


class SmolAgentsAdapter(ToolAdapter):
    """Adapter for the `smolagents` framework.

    Note that the `smolagents` framework do not support async tools at this time so we
    write only the adapt method.
    """

    def adapt(
        self,
        func: Callable[[dict | None], mcp.types.CallToolResult],
        mcp_tool: mcp.types.Tool,
    ) -> smolagents.Tool:
        # we have to recreate a good function based on on the input schema because
        # the smolagents framework is quite picky.
        json_schema = jsonref.replace_refs(mcp_tool.inputSchema).get("properties", {})

        # Create class template
        # TODO: we use **kwargs -> kwargs in the underlying MCP function not sure if that
        # holds in all cases.
        class_template = f'''
class SmolAgentsTool(smolagents.Tool):
    def __init__(self):
        super().__init__()
        self.name = mcp_tool.name
        self.description = mcp_tool.description
        self.inputs = {{
            k: {{
                "type": v["type"],
                # TODO: use google-docstring-parser to parse description of args and pass it here...
                "description": v.get("description", ""),
            }} for k, v in json_schema.items()
        }}
        self.output_type = "string"
    
    def forward(self, **{next(iter(json_schema))}: dict) -> str:
        """
        Forward method with dynamically generated parameters.
        """
        return func({next(iter(json_schema))}).content[0].text
'''

        # Create namespace and execute the class definition
        namespace = {
            "smolagents": smolagents,
            "func": func,
            "mcp_tool": mcp_tool,
            "json_schema": json_schema,
        }
        exec(class_template, namespace)

        # Get the class from namespace and instantiate it
        tool = namespace["SmolAgentsTool"]()
        return tool


if __name__ == "__main__":
    from mcpadapt.core import MCPAdapt
    from mcp import StdioServerParameters

    with MCPAdapt(
        StdioServerParameters(command="uv", args=["run", "src/echo.py"]),
        SmolAgentsAdapter(),
    ) as tools:
        print(tools)
