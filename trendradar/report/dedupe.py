# coding=utf-8
"""Title-level de-duplication helpers for report rendering."""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple


_PUNCT_RE = re.compile(r"[^\w\u4e00-\u9fff]+", re.UNICODE)
_URL_RE = re.compile(r"https?://\S+")
_NOISE_RE = re.compile(
    r"(快讯|突发|刚刚|最新|重磅|消息称|报道称|回应|道歉|通报|"
    r"shares|stock|stocks|market|markets|update|briefing)",
    re.IGNORECASE,
)


def normalize_title(title: str) -> str:
    """Return a stable comparison key for a news title."""
    if title is None:
        return ""
    text = unicodedata.normalize("NFKC", str(title)).lower()
    text = _URL_RE.sub("", text)
    text = _NOISE_RE.sub("", text)
    text = _PUNCT_RE.sub("", text)
    return text.strip()


def _char_ngrams(text: str, size: int = 2) -> set:
    if len(text) <= size:
        return {text} if text else set()
    return {text[i : i + size] for i in range(len(text) - size + 1)}


def title_similarity(left: str, right: str) -> float:
    """Approximate title similarity without external dependencies."""
    a = normalize_title(left)
    b = normalize_title(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    shorter, longer = sorted((a, b), key=len)
    if len(shorter) >= 10 and shorter in longer:
        return 0.9
    a_grams = _char_ngrams(a)
    b_grams = _char_ngrams(b)
    if not a_grams or not b_grams:
        return 0.0
    return len(a_grams & b_grams) / len(a_grams | b_grams)


class TitleDeduper:
    """Keep first-seen titles and merge duplicate source labels."""

    def __init__(self, threshold: float = 0.62):
        self.threshold = threshold
        self._seen: List[Tuple[str, Dict]] = []

    def add(self, item: Dict, title_key: str = "title") -> Optional[Dict]:
        title = item.get(title_key, "")
        key = normalize_title(title)
        if len(key) < 8:
            unique = dict(item)
            self._seen.append((key, unique))
            return unique

        for seen_key, seen_item in self._seen:
            if len(seen_key) < 8:
                continue
            if title_similarity(key, seen_key) >= self.threshold:
                self._merge_source(seen_item, item)
                return None

        unique = dict(item)
        self._seen.append((key, unique))
        return unique

    @staticmethod
    def _merge_source(existing: Dict, duplicate: Dict) -> None:
        existing["duplicate_count"] = int(existing.get("duplicate_count", 1)) + 1
        sources = [
            existing.get("source_name") or existing.get("feed_name"),
            duplicate.get("source_name") or duplicate.get("feed_name"),
        ]
        parts: List[str] = []
        for source in sources:
            if not source:
                continue
            for part in str(source).split(" / "):
                clean = part.strip()
                if clean and clean not in parts:
                    parts.append(clean)
        if parts:
            existing["source_name"] = " / ".join(parts[:3])
            if len(parts) > 3:
                existing["source_name"] += f" +{len(parts) - 3}"


def dedupe_items(items: List[Dict], threshold: float = 0.62) -> List[Dict]:
    deduper = TitleDeduper(threshold=threshold)
    unique_items: List[Dict] = []
    for item in items:
        unique = deduper.add(item)
        if unique is not None:
            unique_items.append(unique)
    return unique_items
