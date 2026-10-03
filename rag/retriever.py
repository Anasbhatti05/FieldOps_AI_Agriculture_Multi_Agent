import re
from dataclasses import dataclass
from pathlib import Path


DOCUMENTS_DIR = Path(__file__).parent / "documents"


@dataclass(frozen=True)
class Passage:
    text: str
    source: str
    score: int


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", text) if len(token) > 1}


def retrieve(query: str, limit: int = 3) -> list[Passage]:
    query_tokens = _tokens(query)
    passages: list[Passage] = []
    for document in sorted(DOCUMENTS_DIR.glob("*.md")):
        for paragraph in document.read_text(encoding="utf-8").split("\n\n"):
            text = paragraph.strip()
            if not text or text.startswith("#"):
                continue
            overlap = query_tokens & _tokens(text)
            if overlap:
                passages.append(Passage(text=text, source=document.name, score=len(overlap)))
    return sorted(passages, key=lambda item: (-item.score, item.source))[:limit]