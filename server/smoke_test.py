"""
In-process smoke test: confirms the server starts and all four tools are
registered and callable via the MCP SDK's in-process Client test pattern
(no subprocess, no live DB required for this check — see DoD item 3).
"""

from __future__ import annotations

import asyncio

from mcp.shared.memory import create_connected_server_and_client_session

from server.main import mcp


async def main() -> None:
    async with create_connected_server_and_client_session(mcp._mcp_server) as client:
        tools = await client.list_tools()
        names = sorted(t.name for t in tools.tools)
        expected = sorted(
            ["append_claim", "get_claim_status", "check_substantiation", "classify_claim_risk"]
        )
        assert names == expected, f"expected {expected}, got {names}"
        print(f"all four tools registered: {names}")


if __name__ == "__main__":
    asyncio.run(main())
