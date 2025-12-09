from collections import deque
from typing import List, Set, Optional
import httpx
from bs4 import BeautifulSoup

from ncloud_docs_mcp.config import FIN_START_URL, HTTP_TIMEOUT, USER_AGENT


class FinCrawler:
    """
    금융 사용 가이드 전체를 BFS로 크롤링하여 /docs 내부 URL 목록을 수집합니다.
    """

    def __init__(self) -> None:
        self.start_url = FIN_START_URL
        self.visited: Set[str] = set()
        self.headers = {"User-Agent": USER_AGENT}

    def fetch(self, url: str) -> str:
        with httpx.Client(
            timeout=HTTP_TIMEOUT,
            headers=self.headers,
            follow_redirects=True,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text

    def _normalize_url(self, href: str) -> Optional[str]:
        """
        /docs 경로만 대상으로 하고,
        #fragment 가 붙은 경우 fragment 는 제거한다.
        그 외 도메인/경로는 None 반환.
        """
        if not href:
            return None

        # 페이지 내 앵커만 있는 경우
        if href.startswith("#"):
            return None

        # 절대 경로 형태
        if href.startswith("https://guide-fin.ncloud-docs.com/docs"):
            base, *_ = href.split("#", 1)
            return base

        # /docs 로 시작하는 상대경로
        if href.startswith("/docs"):
            base, *_ = href.split("#", 1)
            return f"https://guide-fin.ncloud-docs.com{base}"

        # 기타 도메인/경로는 제외
        return None

    def extract_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []

        for a in soup.find_all("a", href=True):
            url = self._normalize_url(a["href"])
            if url:
                links.append(url)

        # 중복 제거
        return list(dict.fromkeys(links))

    def crawl(self) -> List[str]:
        """
        BFS 로 모든 /docs 페이지 URL 추출.
        """
        queue = deque([self.start_url])
        result: List[str] = []

        while queue:
            url = queue.popleft()
            if url in self.visited:
                continue
            self.visited.add(url)

            try:
                html = self.fetch(url)
            except Exception as e:
                print(f"[WARN] failed to fetch: {url} ({e})")
                continue

            result.append(url)

            next_links = self.extract_links(html)
            for link in next_links:
                if link not in self.visited:
                    queue.append(link)

        return result
