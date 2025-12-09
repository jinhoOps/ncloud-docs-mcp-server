from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


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
        self.ensure_collection()
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
