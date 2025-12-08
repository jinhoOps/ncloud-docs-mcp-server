
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


class NcpQdrantClient:
    """
    Naver Cloud 문서용 Qdrant 래퍼.

    추후에:
    - payload 스키마를 DocumentSection, SearchResult 모델과 연결
    - platform, guide_type 등 필터 조건 추가
    """

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "ncp_docs_fin_usage",
        vector_dim: int = 1536,
    ) -> None:
        self.url = url
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.client = QdrantClient(url=self.url)

    def ensure_collection(self) -> None:
        """
        컬렉션이 없으면 생성하고, 있으면 그대로 둡니다.
        """
        collections = self.client.get_collections()
        names = [c.name for c in collections.collections]

        if self.collection_name in names:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_dim,
                distance=Distance.COSINE,
            ),
        )

    def upsert_sections(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[Any]] = None,
    ) -> None:
        """
        섹션 단위 벡터와 payload 를 업서트합니다.

        vectors: 임베딩 벡터 리스트
        payloads: 각 섹션에 대한 메타데이터 (platform, url, title, section, text 등)
        ids: 선택적으로 포인트 ID 리스트 (없으면 자동 생성)
        """
        if len(vectors) != len(payloads):
            raise ValueError("vectors 길이와 payloads 길이가 일치해야 합니다.")

        self.ensure_collection()

        self.client.upsert(
            collection_name=self.collection_name,
            points={
                "ids": ids,
                "vectors": vectors,
                "payloads": payloads,
            },
        )

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        쿼리 벡터로 Qdrant 검색을 수행합니다.

        반환값: payload 와 score 를 포함하는 딕셔너리 리스트 (MVP에서는 단순 딕셔너리)
        """
        self.ensure_collection()

        # 필터는 일단 TODO (platform=fin 같은 조건은 추후 추가)
        qdrant_filter = None

        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
        )

        output: List[Dict[str, Any]] = []
        for hit in result:
            output.append(
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
            )

        return output
