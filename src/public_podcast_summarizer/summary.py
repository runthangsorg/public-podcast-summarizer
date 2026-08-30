"""Deterministic publisher-notes summarization with strict output bounds."""

from __future__ import annotations

import re


def summarize_notes(
    notes: str, *, max_points: int = 3, max_chars: int = 240
) -> list[str]:
    if not 1 <= max_points <= 10 or not 40 <= max_chars <= 500:
        raise ValueError("summary bounds are outside the supported range")
    clean = re.sub(r"\s+", " ", str(notes or "")).strip()
    if not clean:
        return ["No publisher notes were provided."]
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", clean)
        if sentence.strip()
    ]
    if not sentences:
        sentences = [clean]
    bounded = []
    for sentence in sentences[:max_points]:
        if len(sentence) <= max_chars:
            bounded.append(sentence)
            continue
        prefix = sentence[: max_chars - 3].rsplit(" ", 1)[0].rstrip(" ,;:")
        bounded.append((prefix or sentence[: max_chars - 3]).rstrip() + "...")
    return bounded
