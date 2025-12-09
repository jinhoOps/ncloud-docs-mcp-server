from typing import List, Dict
from bs4 import BeautifulSoup


class ContentExtractor:
    """
    guide-fin 페이지 HTML에서 본문 영역을 추출하고,
    h1/h2/h3 기준 섹션 리스트를 만듭니다.
    """

    def extract_sections(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")

        # 1차는 최대한 안전하게 전체 문서 기준으로 섹션 추출
        # 나중에 NCP docs 구조 확인해서 main/article/div 로 좁힐 예정
        content = soup

        sections: List[Dict[str, str]] = []

        current_title = None
        current_text_parts: List[str] = []

        # 섹션 헤더: h1, h2, h3
        for el in content.find_all(["h1", "h2", "h3", "p", "li", "pre", "code"]):
            if el.name in ["h1", "h2", "h3"]:
                # 이전 섹션이 있으면 저장
                if current_title and current_text_parts:
                    sections.append(
                        {
                            "section": current_title,
                            "text": "\n".join(current_text_parts).strip(),
                        }
                    )

                current_title = el.get_text(strip=True)
                current_text_parts = []
            else:
                text = el.get_text(strip=True)
                if text:
                    current_text_parts.append(text)

        # 마지막 섹션
        if current_title and current_text_parts:
            sections.append(
                {
                    "section": current_title,
                    "text": "\n".join(current_text_parts).strip(),
                }
            )

        # 혹시 아무 섹션도 못 뽑았으면 전체 텍스트를 하나의 섹션으로 반환
        if not sections:
            body_text = soup.get_text(separator="\n", strip=True)
            if body_text:
                sections.append(
                    {
                        "section": "본문",
                        "text": body_text,
                    }
                )

        return sections
