from typing import Any, Dict, List
import httpx

from ncloud_docs_mcp.indexer.embedder import DummyEmbedder
from ncloud_docs_mcp.indexer.extractor import ContentExtractor
from ncloud_docs_mcp.vector.qdrant_client import NcpQdrantClient
from ncloud_docs_mcp.models.search import SearchResult
from ncloud_docs_mcp.config import HTTP_TIMEOUT, USER_AGENT


def normalize_platform(platform: str) -> str:
    platform = (platform or "").lower()
    if platform in ("fin", "financial"):
        return "fin"
    if platform in ("gov", "government"):
        return "gov"
    return "public"


def detect_platform_from_url(url: str) -> str:
    if "guide-fin" in url or "api-fin" in url:
        return "fin"
    if "guide-gov" in url or "api-gov" in url:
        return "gov"
    return "public"


def ncp_search_docs(
    platform: str,
    query: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    platform = normalize_platform(platform)

    embedder = DummyEmbedder()
    qdrant = NcpQdrantClient()

    # 쿼리 한 개 → 벡터 한 개
    query_vec = embedder.embed([query])[0]

    hits: List[Dict[str, Any]] = qdrant.search(
        query_vector=query_vec,
        top_k=top_k,
        filters=None,
    )

    items: List[Dict[str, Any]] = []
    for hit in hits:
        payload = hit.get("payload") or {}

        title = payload.get("title", "")
        url = payload.get("url", "")
        section = payload.get("section", "")
        text = payload.get("text", "")
        snippet = text[:200]

        items.append(
            {
                "title": title,
                "url": url,
                "section": section,
                "snippet": snippet,
                "score": hit.get("score", 0.0),
                "platform": payload.get("platform", platform),
            }
        )

    return {
        "platform": platform,
        "query": query,
        "top_k": top_k,
        "results": items,
    }


def ncp_read_doc(url: str) -> Dict[str, Any]:
    platform = detect_platform_from_url(url)

    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(timeout=HTTP_TIMEOUT, headers=headers, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text

    extractor = ContentExtractor()
    sections = extractor.extract_sections(html)

    lines: List[str] = []
    for sec in sections:
        title = sec["section"]
        text = sec["text"]
        lines.append(f"## {title}")
        lines.append("")
        lines.append(text)
        lines.append("")

    markdown_body = "\n".join(lines).strip()

    return {
        "url": url,
        "platform": platform,
        "title": "(추후추출)",
        "markdown_body": markdown_body,
    }
