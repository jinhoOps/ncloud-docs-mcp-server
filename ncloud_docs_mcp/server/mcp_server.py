
from typing import Any, Dict


try:
    # 실제 MCP Python SDK 패키지명에 맞게 수정해야 합니다.
    # 예시:
    # from mcp.server import Server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None  # type: ignore[misc]


def ncp_search_docs_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP 툴: ncp_search_docs

    입력:
      - platform: "public" | "fin" | "gov"
      - query: str
      - top_k: int

    현재는 스켈레톤이므로, 실제 검색 대신 echo 형태의 응답만 반환합니다.
    """
    platform = params.get("platform", "fin")
    query = params.get("query", "")
    top_k = int(params.get("top_k", 5))

    # TODO:
    # 1. query 임베딩 계산
    # 2. Qdrant 검색 호출
    # 3. SearchResult 리스트를 MCP 응답 포맷으로 변환
    return {
        "platform": platform,
        "query": query,
        "top_k": top_k,
        "results": [],
        "message": "ncp_search_docs: 아직 실제 검색 로직은 구현되지 않았습니다.",
    }


def ncp_read_doc_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP 툴: ncp_read_doc

    입력:
      - url: str

    현재는 스켈레톤이므로, 실제 HTML 파싱 대신 단순 메시지만 반환합니다.
    """
    url = params.get("url", "")

    # TODO:
    # 1. URL 기반 platform 판별
    # 2. HTML GET
    # 3. 본문 추출 및 markdown 변환
    return {
        "url": url,
        "platform": "fin",  # 임시 값
        "title": "(미구현) 제목",
        "markdown_body": "ncp_read_doc: 아직 HTML → markdown 변환 로직은 구현되지 않았습니다.",
    }


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

    # TODO: MCP SDK 실제 사용 예제에 맞게 구현
    # 아래는 개략적인 의사 코드입니다.

    # server = Server("ncloud-docs-mcp-server")
    #
    # @server.tool("ncp_search_docs")
    # def ncp_search_docs_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    #     return ncp_search_docs_tool(params)
    #
    # @server.tool("ncp_read_doc")
    # def ncp_read_doc_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    #     return ncp_read_doc_tool(params)
    #
    # server.run_stdio()

    print("run_stdio_server: MCP 서버 로직은 아직 구현되지 않았습니다. MCP SDK 예제에 맞게 Server 초기화와 툴 등록을 추가해 주세요.")


def main() -> None:
    run_stdio_server()


if __name__ == "__main__":
    main()
