"""Small rule-based Vietnamese sentiment classifier."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


POSITIVE_WORDS = {
    "tot",
    "tốt",
    "hay",
    "ngon",
    "thich",
    "thích",
    "yeu",
    "yêu",
    "tuyet",
    "tuyệt",
    "xuat sac",
    "xuất sắc",
    "hai long",
    "hài lòng",
    "de thuong",
    "dễ thương",
    "nhanh",
    "huu ich",
    "hữu ích",
    "on ap",
    "ổn áp",
    "re",
    "rẻ",
    "giam gia",
    "giảm giá",
}

NEGATIVE_WORDS = {
    "te",
    "tệ",
    "xau",
    "xấu",
    "chan",
    "chán",
    "loi",
    "lỗi",
    "cham",
    "chậm",
    "dat",
    "đắt",
    "kem",
    "kém",
    "khong thich",
    "không thích",
    "that vong",
    "thất vọng",
    "buc minh",
    "bực mình",
    "can cai thien",
    "cần cải thiện",
    "phan nan",
    "phàn nàn",
    "huy",
    "huỷ",
}

NEGATORS = {"khong", "không", "chua", "chưa", "chang", "chẳng"}


@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text or "")).lower()
    text = re.sub(r"[^\w\sÀ-ỹ]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(rf"(^|\s){re.escape(phrase)}($|\s)", text) is not None


def analyze_sentiment(text: str) -> SentimentResult:
    """Classify a Vietnamese/ASCII-Vietnamese comment into positive/neutral/negative."""

    normalized = _normalize_text(text)
    if not normalized:
        return SentimentResult("neutral", 0.0)

    positive = sum(1 for word in POSITIVE_WORDS if _contains_phrase(normalized, word))
    negative = sum(1 for word in NEGATIVE_WORDS if _contains_phrase(normalized, word))

    tokens = normalized.split()
    for index, token in enumerate(tokens[:-1]):
        if token in NEGATORS:
            window = " ".join(tokens[index + 1 : index + 4])
            if any(_contains_phrase(window, word) for word in POSITIVE_WORDS):
                positive = max(0, positive - 1)
                negative += 1
            elif any(_contains_phrase(window, word) for word in NEGATIVE_WORDS):
                negative = max(0, negative - 1)
                positive += 1

    raw_score = positive - negative
    if raw_score > 0:
        return SentimentResult("positive", min(1.0, round(raw_score / 3, 2)))
    if raw_score < 0:
        return SentimentResult("negative", max(-1.0, round(raw_score / 3, 2)))
    return SentimentResult("neutral", 0.0)
