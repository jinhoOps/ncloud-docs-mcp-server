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
        MVP 1차용: Qdrant에서 payload만 가져오고, score는 항상 0.0 으로 고정한다.
        (qdrant-client 버전마다 score 타입이 달라서 발생하는 오류를 피하기 위함)
        """
        self.ensure_collection()

        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=None,   # filters는 아직 미사용
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        output: List[Dict[str, Any]] = []

        for idx, point in enumerate(result):
            # point 타입이 버전에 따라 ScoredPoint, 튜플, dict 등 다양할 수 있으므로
            # payload만 최대한 안정적으로 뽑고 나머지는 최소한으로 처리한다.

            payload: Dict[str, Any] = {}

            # 1) 객체 스타일 (ScoredPoint)
            if hasattr(point, "payload"):
                payload = getattr(point, "payload", {}) or {}
                pid = getattr(point, "id", idx)

            # 2) dict 스타일
            elif isinstance(point, dict):
                payload = point.get("payload", {}) or {}
                pid = point.get("id", idx)

            # 3) 튜플/리스트 스타일 (id, score, payload) 혹은 (ScoredPoint, payload)
            elif isinstance(point, (tuple, list)) and point:
                # (ScoredPoint, payload_dict)
                if hasattr(point[0], "payload"):
                    pid = getattr(point[0], "id", idx)
                    payload = getattr(point[0], "payload", None) or (point[1] if len(point) > 1 else {})
                else:
                    # (id, score, payload) 형태 가정
                    pid = point[0]
                    payload = point[2] if len(point) > 2 else {}

            else:
                pid = idx
                payload = {}

            output.append(
                {
                    "id": pid,
                    "score": 0.0,        # 여기서 score 는 완전히 무시 (MVP 단계)
                    "payload": payload,
                }
            )

        return output