"""An example of using MCPAdapt with the smolagents framework to query pubmed papers.

Note this is just a demo MCP server that I implemented for the purpose of this example.
It only provide a single tool to search amongst pubmed papers abstracts.
"""

import os

from mcp import StdioServerParameters
from smolagents import CodeAgent, HfApiModel

from mcpadapt.core import MCPAdapt
from mcpadapt.smolagents_adapter import SmolAgentsAdapter

with MCPAdapt(
    StdioServerParameters(
        command="uvx",
        args=["--quiet", "pubmedmcp@0.1.3"],
        env={"UV_PYTHON": "3.12", **os.environ},
    ),
    SmolAgentsAdapter(),
) as tools:
    # print(tools[0](request={"term": "efficient treatment for hangover"}))
    agent = CodeAgent(tools=tools, model=HfApiModel())
    agent.run("Find studies about hangover?")
