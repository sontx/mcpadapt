from textwrap import dedent

import pytest
from mcp import StdioServerParameters

from mcpadapt.core import MCPAdapt
from mcpadapt.langchain_adapter import LangChainAdapter


@pytest.fixture
def echo_server_script():
    return dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server")

        @mcp.tool()
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"
        
        mcp.run()
        '''
    )


@pytest.fixture
def echo_server_sse_script():
    return dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server", host="127.0.0.1", port=8000)

        @mcp.tool()
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"

        mcp.run("sse")
        '''
    )


@pytest.fixture
async def echo_sse_server(echo_server_sse_script):
    import subprocess
    import time

    # Start the SSE server process with its own process group
    process = subprocess.Popen(
        ["python", "-c", echo_server_sse_script],
    )

    # Give the server a moment to start up
    time.sleep(1)

    try:
        yield {"url": "http://127.0.0.1:8000/sse"}
    finally:
        # Clean up the process when test is done
        process.kill()
        process.wait()


@pytest.mark.asyncio
async def test_basic_async(echo_server_script):
    async with MCPAdapt(
        StdioServerParameters(
            command="uv", args=["run", "python", "-c", echo_server_script]
        ),
        LangChainAdapter(),
    ) as tools:
        assert len(tools) == 1  # we expect one tool as defined above
        assert tools[0].name == "echo_tool"  # we expect the tool to be named echo_tool
        response = await tools[0].ainvoke("hello")
        assert response == "Echo: hello"  # we expect the tool to return "Echo: hello"


@pytest.mark.asyncio
async def test_basic_async_sse(echo_sse_server):
    sse_serverparams = echo_sse_server
    async with MCPAdapt(
        sse_serverparams,
        LangChainAdapter(),
    ) as tools:
        assert len(tools) == 1  # we expect one tool as defined above
        assert tools[0].name == "echo_tool"  # we expect the tool to be named echo_tool
        response = await tools[0].ainvoke("hello")
        assert response == "Echo: hello"  # we expect the tool to return "Echo: hello"


def test_basic_sync(echo_server_script):
    with MCPAdapt(
        StdioServerParameters(
            command="uv", args=["run", "python", "-c", echo_server_script]
        ),
        LangChainAdapter(),
    ) as tools:
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"
        assert tools[0].invoke("hello") == "Echo: hello"


def test_basic_sync_sse(echo_sse_server):
    sse_serverparams = echo_sse_server
    with MCPAdapt(
        sse_serverparams,
        LangChainAdapter(),
    ) as tools:
        assert len(tools) == 1


def test_tool_name_with_dashes():
    mcp_server_script = dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server")

        @mcp.tool(name="echo-tool")
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"
        
        mcp.run()
        '''
    )
    with MCPAdapt(
        StdioServerParameters(
            command="uv", args=["run", "python", "-c", mcp_server_script]
        ),
        LangChainAdapter(),
    ) as tools:
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"
        assert tools[0].invoke("hello") == "Echo: hello"


def test_tool_name_with_keyword():
    mcp_server_script = dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server")

        @mcp.tool(name="def")
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"
        
        mcp.run()
        '''
    )
    with MCPAdapt(
        StdioServerParameters(
            command="uv", args=["run", "python", "-c", mcp_server_script]
        ),
        LangChainAdapter(),
    ) as tools:
        assert len(tools) == 1
        assert tools[0].name == "def_"
        assert tools[0].invoke("hello") == "Echo: hello"
