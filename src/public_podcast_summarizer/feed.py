"""Parse bounded RSS/Atom metadata without downloading podcast audio."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit, urlunsplit


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _text(value: Any, *, limit: int) -> str:
    parser = _TextExtractor()
    parser.feed(html.unescape(str(value or "")))
    clean = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return clean[:limit]


def _public_url(value: Any) -> str:
    parts = urlsplit(str(value or "").strip()[:2048])
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(node: ET.Element, names: set[str]) -> str:
    for child in node:
        if _local_name(child.tag) in names and child.text:
            return child.text
    return ""


@dataclass(frozen=True)
class Episode:
    podcast: str
    title: str
    published: str
    notes: str
    link: str

    def to_public_dict(self) -> dict[str, str]:
        return {
            "podcast": self.podcast,
            "title": self.title,
            "published": self.published,
            "notes": self.notes,
            "link": self.link,
            "review_status": "publisher_metadata_only",
        }


def parse_feed(payload: bytes, *, max_episodes: int = 3) -> tuple[Episode, ...]:
    if not 1 <= max_episodes <= 50:
        raise ValueError("max_episodes must be between 1 and 50")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError("invalid XML feed") from exc

    channel = next(
        (node for node in root.iter() if _local_name(node.tag) in {"channel", "feed"}),
        root,
    )
    podcast = _text(_child_text(channel, {"title"}), limit=160)
    candidates = [
        node for node in channel.iter() if _local_name(node.tag) in {"item", "entry"}
    ]
    episodes = []
    for node in candidates[:max_episodes]:
        title = _text(_child_text(node, {"title"}), limit=240)
        notes = _text(
            _child_text(node, {"description", "summary", "content"}), limit=20_000
        )
        published = _text(
            _child_text(node, {"pubdate", "published", "updated"}), limit=80
        )
        link = _child_text(node, {"link"})
        if not link:
            for child in node:
                if _local_name(child.tag) == "link":
                    link = child.attrib.get("href", "")
                    if link:
                        break
        if title:
            episodes.append(
                Episode(
                    podcast=podcast,
                    title=title,
                    published=published,
                    notes=notes,
                    link=_public_url(link),
                )
            )
    return tuple(episodes)
