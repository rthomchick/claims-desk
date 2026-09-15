"""
In-process smoke test: confirms the server starts and all seven tools are
registered and callable via the MCP SDK's in-process Client test pattern
(no subprocess, no live DB required for this check).
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
            [
                "append_claim",
                "append_ruling",
                "check_substantiation",
                "classify_claim_risk",
                "delete_claim",
                "get_claim_status",
                "list_claims",
            ]
        )
        assert names == expected, f"expected {expected}, got {names}"
        print(f"all seven tools registered: {names}")


if __name__ == "__main__":
    asyncio.run(main())
