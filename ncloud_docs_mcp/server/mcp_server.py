# ncloud_docs_mcp/server/mcp_server.py

from typing import Any, Dict

from mcp.server.fastmcp import FastMCP  # MCP Python SDK
from ncloud_docs_mcp.server.tools import ncp_search_docs, ncp_read_doc

# Claude/Desktop 에서 보일 MCP 서버 이름
mcp = FastMCP("ncloud-docs-mcp-server")


@mcp.tool()
async def search_docs(
    platform: str,
    query: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    NCP 문서 검색 도구 (MCP Tool)
    - platform: "public" | "fin" | "gov"
    - query   : 검색어
    - top_k   : 최대 결과 개수
    """
    return ncp_search_docs(platform=platform, query=query, top_k=top_k)


@mcp.tool()
async def read_doc(
    url: str,
) -> Dict[str, Any]:
    """
    NCP 단일 문서 읽기 도구 (MCP Tool)
    - url: NCP 문서 URL (예: https://guide-fin.ncloud-docs.com/docs/server-overview)
    """
    return ncp_read_doc(url)


def main() -> None:
    """
    STDIO 기반 MCP 서버 시작 엔트리포인트.

    중요:
    - MCP 서버는 JSON-RPC를 stdout/stdin으로 주고받으므로,
      이 파일 안에서는 절대 print()로 stdout에 로그를 찍지 말 것.
      (로그는 필요하면 logging + stderr 핸들러로 보내야 함)
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
