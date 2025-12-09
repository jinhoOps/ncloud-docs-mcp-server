from typing import List
import hashlib


class DummyEmbedder:
    """
    MVP 초기 단계에서는 임시로 해시 기반 숫자를 만들어 벡터처럼 사용합니다.
    나중에 실제 임베딩 API로 교체할 예정입니다.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for t in texts:
            # 단순 해시 → 고정 길이 16차원 벡터
            h = hashlib.md5(t.encode()).digest()
            vec = [float(b) / 255.0 for b in h[:16]]
            vectors.append(vec)
        return vectors
