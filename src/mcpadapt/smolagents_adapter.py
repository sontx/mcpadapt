"""This module implements the SmolAgents adapter.

SmolAgents do not support async tools, so this adapter will only work with the sync
context manager.

Example Usage:
>>> with MCPAdapt(StdioServerParameters(command="uv", args=["run", "src/echo.py"]), SmolAgentAdapter()) as tools:
>>>     print(tools)
"""

from typing import Callable

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
        # because CallToolResult is not usually what we expect we return here the content
        # of the first message in the content list.
        def forward(arguments: dict | None) -> str:
            call_tool_result = func(arguments)
            return call_tool_result.content[0].text

        return type(
            snake_to_camel(mcp_tool.name),
            (smolagents.Tool,),
            {
                "name": mcp_tool.name,
                "description": mcp_tool.description,
                "inputs": {
                    k: {
                        "type": v["type"],
                        # TODO: use google-docstring-parser to parse description of args and pass it here...
                        # "description": v["description"],
                    }
                    for k, v in mcp_tool.inputSchema.get("properties", {}).items()
                },
                # TODO: use google-docstring-parser to parse description of return type and pass it here...
                "output_type": str,
                "forward": forward,
            },
        )


if __name__ == "__main__":
    from mcpadapt.core import MCPAdapt
    from mcp import StdioServerParameters

    with MCPAdapt(
        StdioServerParameters(command="uv", args=["run", "src/echo.py"]),
        SmolAgentsAdapter(),
    ) as tools:
        print(tools)
