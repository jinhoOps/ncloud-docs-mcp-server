from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    section: str
    snippet: str
    score: float
    platform: str
