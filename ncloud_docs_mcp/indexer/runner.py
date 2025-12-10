from ncloud_docs_mcp.indexer.crawler import FinCrawler
from ncloud_docs_mcp.indexer.extractor import ContentExtractor
from ncloud_docs_mcp.indexer.embedder import DummyEmbedder
from ncloud_docs_mcp.vector.qdrant_client import NcpQdrantClient


def run_fin_index() -> None:
    print("=== run_fin_index: 금융 문서 전체 인덱싱 시작 ===")

    crawler = FinCrawler()
    extractor = ContentExtractor()
    embedder = DummyEmbedder()
    qdrant = NcpQdrantClient()

    urls = crawler.crawl()
    print(f"총 {len(urls)}개의 URL 수집됨")

    # 실제 어떤 URL들이 들어왔는지 상위 몇 개 찍어보기
    for i, u in enumerate(urls[:20]):
        print(f"  URL[{i}]: {u}")

    # 최대 N개만 인덱싱 (개발 중에는 작은 수로 제한)
    max_urls = 100
    target_urls = urls[:max_urls]
    print(f"앞 {len(target_urls)}개의 URL만 인덱싱 진행")

    for url in target_urls:
        print(f"[PROCESS] {url}")

        try:
            html = crawler.fetch(url)
            print("  fetch OK")
        except Exception as e:
            print(f"  [WARN] fetch 실패: {e}")
            continue

        sections = extractor.extract_sections(html)
        print(f"  섹션 수: {len(sections)}")

        if not sections:
            print("  섹션 없음 → skip")
            continue

        texts = [sec["text"] for sec in sections]
        vectors = embedder.embed(texts)
        print(f"  벡터 수: {len(vectors)}")

        payloads = []
        for sec in sections:
            payloads.append(
                {
                    "platform": "fin",
                    "guide_type": "usage",
                    "url": url,
                    "title": "(추후추출)",
                    "section": sec["section"],
                    "text": sec["text"],
                }
            )

        print(f"  payload 수: {len(payloads)}")

        try:
            qdrant.upsert_sections(vectors=vectors, payloads=payloads)
            print("  Qdrant upsert 완료")
        except Exception as e:
            print(f"  [ERROR] Qdrant upsert 실패: {e}")
            break

    print("=== run_fin_index: 완료 ===")


if __name__ == "__main__":
    run_fin_index()
