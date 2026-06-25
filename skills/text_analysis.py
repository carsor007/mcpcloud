"""Text analysis skills — no external dependencies required.

Skills:
- summarize          : extractive summary (top scored sentences)
- extract_keywords   : top N keywords by frequency, stopwords filtered
- classify_sentiment : positive / neutral / negative with confidence score

Copy this file, rename it, and swap in your own logic to build new skills.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict

from registry import SkillResult, get_registry

_STOPWORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","could","should","may","might",
    "i","you","he","she","it","we","they","me","him","her","us","them",
    "my","your","his","its","our","their","this","that","these","those",
    "not","no","so","if","as","up","out","about","into","than","then",
    "there","when","where","who","which","what","how","all","each","also",
    "just","more","can","any","some","such","now","only","same","very",
}

_NEG_WORDS = {
    "bad","terrible","awful","horrible","poor","disappointing","broken",
    "fail","failed","error","issue","problem","bug","slow","wrong",
    "unhappy","frustrated","angry","annoying","useless","worst","hate",
    "cannot","never","lack","missing","difficult","confusing","complicated",
}

_POS_WORDS = {
    "good","great","excellent","amazing","awesome","fantastic","perfect",
    "helpful","fast","easy","simple","love","wonderful","brilliant",
    "outstanding","happy","pleased","satisfied","thank","works","solved",
    "clear","clean","nice","best","impressive","smooth","reliable","quick",
    "intuitive","powerful","efficient","seamless","solid","robust",
}


def _sentences(text: str):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _tokens(text: str):
    return [
        w for w in re.findall(r'\b[a-z]+\b', text.lower())
        if w not in _STOPWORDS and len(w) > 2
    ]


async def summarize(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Extractive summary — return the top N most informative sentences.

    Input: { "text": "...", "sentences": 3 }
    """
    text = input.get("text", "")
    n = min(max(int(input.get("sentences", 3)), 1), 10)

    if not text:
        return SkillResult(success=False, output={}, error="'text' is required")

    sents = _sentences(text)
    if len(sents) <= n:
        return SkillResult(success=True, output={
            "summary": text,
            "original_sentences": len(sents),
            "summary_sentences": len(sents),
        })

    word_freq = Counter(_tokens(text))

    def score(s: str) -> float:
        words = _tokens(s)
        return sum(word_freq[w] for w in words) / max(len(words), 1)

    scored = sorted(enumerate(sents), key=lambda x: score(x[1]), reverse=True)
    top_indices = sorted(i for i, _ in scored[:n])
    summary = " ".join(sents[i] for i in top_indices)

    return SkillResult(success=True, output={
        "summary": summary,
        "original_sentences": len(sents),
        "summary_sentences": n,
    })


async def extract_keywords(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Extract the top N keywords by frequency, filtering common stopwords.

    Input: { "text": "...", "limit": 10 }
    """
    text = input.get("text", "")
    limit = min(max(int(input.get("limit", 10)), 1), 50)

    if not text:
        return SkillResult(success=False, output={}, error="'text' is required")

    counts = Counter(_tokens(text))
    total = sum(counts.values()) or 1
    keywords = [
        {
            "keyword": word,
            "count": count,
            "frequency": round(count / total, 4),
        }
        for word, count in counts.most_common(limit)
    ]

    return SkillResult(success=True, output={
        "keywords": keywords,
        "total_words": total,
        "unique_words": len(counts),
    })


async def classify_sentiment(input: Dict[str, Any], context: Dict[str, Any]) -> SkillResult:
    """Classify text as positive, neutral, or negative with a confidence score.

    Input: { "text": "..." }
    Output: { "label": "positive"|"neutral"|"negative", "score": -1.0..1.0, "confidence": 0..1 }
    """
    text = input.get("text", "")
    if not text:
        return SkillResult(success=False, output={}, error="'text' is required")

    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    pos_hits = words & _POS_WORDS
    neg_hits = words & _NEG_WORDS
    pos, neg = len(pos_hits), len(neg_hits)
    total = pos + neg

    if total == 0:
        return SkillResult(success=True, output={
            "label": "neutral",
            "score": 0.0,
            "confidence": 0.5,
            "matched_positive": [],
            "matched_negative": [],
        })

    score = round((pos - neg) / total, 3)
    confidence = round(min(total / 5, 1.0) * 0.5 + 0.5, 3)
    label = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"

    return SkillResult(success=True, output={
        "label": label,
        "score": score,
        "confidence": confidence,
        "matched_positive": sorted(pos_hits),
        "matched_negative": sorted(neg_hits),
    })


def register_all() -> None:
    registry = get_registry()

    registry.register(
        "text_analysis", "summarize", summarize,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "Text to summarize."},
                "sentences": {"type": "integer", "description": "Number of sentences to return (default 3, max 10)."},
            },
        },
    )

    registry.register(
        "text_analysis", "extract_keywords", extract_keywords,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "Text to extract keywords from."},
                "limit": {"type": "integer", "description": "Max keywords to return (default 10)."},
            },
        },
    )

    registry.register(
        "text_analysis", "classify_sentiment", classify_sentiment,
        schema={
            "type": "object",
            "required": ["text"],
            "properties": {
                "text": {"type": "string", "description": "Text to classify."},
            },
        },
    )
