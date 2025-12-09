import os
from dotenv import load_dotenv

load_dotenv()

# 금융 사용 가이드 시작 URL
FIN_START_URL = "https://guide-fin.ncloud-docs.com/docs"

# Qdrant 설정
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_FIN_USAGE = os.getenv("QDRANT_COLLECTION_FIN_USAGE", "ncp_docs_fin_usage")

# 임베딩 모델 이름 (추후 실제 모델로 교체 예정)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

# HTTP 요청 옵션
HTTP_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
