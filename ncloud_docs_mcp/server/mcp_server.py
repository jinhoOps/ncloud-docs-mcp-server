from typing import Any, Dict

from ncloud_docs_mcp.server.tools import ncp_search_docs, ncp_read_doc


try:
    # MCP Python SDK 패키지명에 맞게 수정해야 합니다.
    # 예시: from mcp.server import Server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None  # type: ignore[misc]


def ncp_search_docs_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    platform = params.get("platform", "fin")
    query = params.get("query", "")
    top_k = int(params.get("top_k", 5))

    return ncp_search_docs(platform=platform, query=query, top_k=top_k)


def ncp_read_doc_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    url = params.get("url", "")
    return ncp_read_doc(url=url)


def run_stdio_server() -> None:
    """
    MCP stdio 서버 실행 엔트리.

    실제 MCP SDK 를 사용할 때:
    - Server 인스턴스 생성
    - ncp_search_docs, ncp_read_doc 툴 등록
    - stdio 루프 실행
    """
    if not MCP_AVAILABLE:
        print("MCP Python SDK 를 찾을 수 없습니다. 해당 패키지를 설치한 뒤 import 부분을 수정해 주세요.")
        return

    # TODO: MCP SDK 실제 사용 예제에 맞게 Server 초기화와 툴 등록을 구현하세요.
    print("run_stdio_server: MCP 서버 로직은 아직 구현되지 않았습니다.")


def main() -> None:
    run_stdio_server()


if __name__ == "__main__":
    main()
