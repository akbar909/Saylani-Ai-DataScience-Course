import re
from collections import Counter

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "is",
    "are",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "this",
    "that",
    "by",
    "from",
    "as",
    "at",
    "be",
    "it",
    "its",
    "was",
    "were",
    "will",
    "has",
    "have",
    "had",
    "about",
}

POSITIVE_WORDS = {
    "growth",
    "rise",
    "profit",
    "improve",
    "innovation",
    "success",
    "strong",
    "gain",
    "positive",
    "opportunity",
}

NEGATIVE_WORDS = {
    "decline",
    "drop",
    "loss",
    "risk",
    "crash",
    "weak",
    "fall",
    "negative",
    "threat",
    "recession",
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", text.lower())


def extract_keywords(text: str, top_k: int = 8) -> list[str]:
    tokens = [t for t in tokenize(text) if t not in STOPWORDS]
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(top_k)]


def sentiment_label(text: str) -> tuple[str, float]:
    tokens = tokenize(text)
    if not tokens:
        return "neutral", 0.0

    pos = sum(1 for token in tokens if token in POSITIVE_WORDS)
    neg = sum(1 for token in tokens if token in NEGATIVE_WORDS)

    score = (pos - neg) / max(len(tokens), 1)
    if score > 0.01:
        return "positive", score
    if score < -0.01:
        return "negative", score
    return "neutral", score
