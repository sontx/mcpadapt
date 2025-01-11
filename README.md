# MCPAdapt

Unlock 650+ MCP servers tools in your favorite agentic framework.

## Installation Instructions

```bash
# with uv
uv add mcpadapt

# or with pip
pip install mcpadapt
```

## Usage

MCPAdapt adapt any MCP servers into tools that you can use right in your agentic workflow:

```python
with MCPAdapt(
    # specify the command to run your favorite MCP server (support also smithery and co.)
    StdioServerParameters(command="uv", args=["run", "src/echo.py"]),

    # specify the adapter you want to use to adapt MCP into your tool in this case smolagents.
    SmolAgentsAdapter(),
) as tools:
    # enjoy your smolagents tools as if you wrote them yourself
    ...
```

MCP Adapt supports Smolagents, [Pydantic.dev, Langchain, Llammaindex and more...]*.

## Contribute

If your favorite agentic framework is missing no problem add it yourself it's quite easy:

1. create a new module in `src/mcpadapt/{name_of_your_framework}_adapter.py`:

```python
class YourFrameworkAdapter(ToolAdapter):
    def adapt(
        self,
        func: Callable[[dict | None], mcp.types.CallToolResult],
        mcp_tool: mcp.types.Tool,
    ) -> YourFramework.Tool:
        # HERE implement how the adapter should convert a simple function and mcp_tool (JSON Schema)
        # into your framework tool. see smolagents_adapter.py for an example
    
    def async_adapt(
        self,
        afunc: Callable[[dict | None], Coroutine[Any, Any, mcp.types.CallToolResult]],
        mcp_tool: mcp.types.Tool,
    ) -> YourFramework.Tool:
        # if your framework supports async function even better use async_adapt.
```

2. and that's it, test that your adapter is working and send us a PR to share it with the world.

