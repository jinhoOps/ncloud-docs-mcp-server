from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client import QdrantClient, models

class NcpQdrantClient:
    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_name: str = "ncp_docs_fin_usage",
        vector_dim: int = 16,
    ) -> None:
        self.url = url
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.client = QdrantClient(url=self.url)

    def ensure_collection(self) -> None:
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
        if len(vectors) != len(payloads):
            raise ValueError("vectors 길이와 payloads 길이가 일치해야 합니다.")

        self.ensure_collection()

        if ids is None:
            ids = list(range(len(vectors)))

        points: List[PointStruct] = []
        for i, (vec, payload) in enumerate(zip(vectors, payloads)):
            points.append(
                PointStruct(
                    id=ids[i],
                    vector=vec,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        
        
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Qdrant query_points 결과(QueryResponse)를 올바르게 파싱해서
        id / score / payload 를 꺼내는 단순한 버전.

        - score 는 현재 MVP 단계에서는 크게 의미 없으므로 그대로 전달만 하고,
          ncp_search_docs 쪽에서는 필요하면 무시해도 된다.
        """
        self.ensure_collection()

        res = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=None,   # filters는 아직 사용 안 함
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # qdrant-client 버전에 따라:
        # - res 가 QueryResponse 이고 res.points 안에 ScoredPoint 리스트가 있는 형태가 일반적
        # - 혹시 구버전이면 res 자체가 리스트일 수도 있음
        points = getattr(res, "points", res)

        output: List[Dict[str, Any]] = []

        for p in points:
            # ScoredPoint 객체 기준
            pid = getattr(p, "id", None)
            score = getattr(p, "score", 0.0)
            payload = getattr(p, "payload", {}) or {}

            # 혹시 dict 형식으로 들어오는 경우 방어
            if isinstance(p, dict):
                pid = p.get("id", pid)
                score = p.get("score", score)
                payload = p.get("payload", payload) or {}

            # id 가 여전히 None이면 index 기반으로라도 채워주기
            if pid is None:
                pid = len(output)

            output.append(
                {
                    "id": pid,
                    "score": float(score) if isinstance(score, (int, float)) else 0.0,
                    "payload": payload,
                }
            )

        return output