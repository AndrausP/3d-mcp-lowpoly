"""End-to-end check of the MCP server over stdio:  python selftest.py"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    p = StdioServerParameters(command=sys.executable, args=["-m", "lowpoly_mcp.server"], cwd=".")
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print([t.name for t in (await s.list_tools()).tools], flush=True)
            res = await s.call_tool("generate_character", {"preset": "Viking_Female", "formats": ["fbx"],
                                                           "animations_from": "Pirate_Male",
                                                           "animations": ["Idle", "Run"]})
            for c in res.content:
                print(c.type, c.text[:300] if c.type == "text" else len(c.data), flush=True)
            res = await s.call_tool("generate_prop", {"prop": "house", "formats": ["glb"]})
            for c in res.content:
                print(c.type, c.text[:200] if c.type == "text" else len(c.data), flush=True)
            res = await s.call_tool("analyze_model", {"path": "Pug"})
            print(res.content[0].text[:200], flush=True)


asyncio.run(main())
