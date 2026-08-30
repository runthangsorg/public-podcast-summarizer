"""Load a bounded XML feed while explicitly refusing media downloads."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from typing import Any, Dict, List, Optional


class SourceError(ValueError):
    """Raised when a feed source is unsafe, too large, or unavailable."""


def load_feed(
    source: str, *, timeout: int = 20, max_bytes: int = 25_000_000
) -> bytes:
    parts = urlsplit(source)
    try:
        if parts.scheme:
            if parts.scheme not in {"http", "https"} or not parts.netloc:
                raise SourceError("only HTTP(S) feed URLs are supported")
            if parts.path.lower().endswith((".mp3", ".m4a", ".wav", ".mp4")):
                raise SourceError("media downloads are not supported")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            request = Request(source, headers=headers)
            with urlopen(request, timeout=timeout) as response:
                payload = response.read(max_bytes + 1)
        else:
            path = Path(source)
            if path.stat().st_size > max_bytes:
                raise SourceError("feed exceeds the byte limit")
            payload = path.read_bytes()
    except SourceError:
        raise
    except OSError as exc:
        raise SourceError("unable to load feed") from exc
    if len(payload) > max_bytes:
        raise SourceError("feed exceeds the byte limit")
    return payload

def _feed_url(value: Any) -> str:
    url = str(value or "").strip()
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise SourceError("feed URL must be public HTTP(S)")
    if parts.path.lower().endswith((".mp3", ".m4a", ".wav", ".mp4")):
        raise SourceError("media downloads are not supported")
    return url


def _label(value: Any, *, name: str, default: str) -> str:
    label = " ".join(str(value or default).split())
    if not label and not default:
        return ""
    if not 1 <= len(label) <= 160:
        raise SourceError(f"{name} is out of bounds")
    return label


def _episode_limit(value: Any) -> int:
    try:
        limit = int(value)
    except (TypeError, ValueError) as exc:
        raise SourceError("max_episodes must be an integer") from exc
    if not 1 <= limit <= 10:
        raise SourceError("max_episodes must be between 1 and 10")
    return limit


def load_feeds_from_config(config_json: Optional[str] = None) -> List[Dict[str, Any]]:
    """Parse strict runtime-only feed configuration without public defaults."""
    if config_json is None:
        config_json = os.environ.get("PODCAST_CONFIG_JSON")
    if not config_json or len(config_json.encode("utf-8")) > 64_000:
        raise SourceError("podcast configuration is empty or oversized")
    try:
        config = json.loads(config_json)
    except json.JSONDecodeError as exc:
        raise SourceError("podcast configuration is not valid JSON") from exc

    default_limit = 1
    if isinstance(config, list):
        raw_feeds = config
    elif isinstance(config, dict):
        if set(config) - {"feeds", "max_episodes"}:
            raise SourceError("podcast configuration contains unknown fields")
        raw_feeds = config.get("feeds")
        default_limit = _episode_limit(config.get("max_episodes", 1))
    else:
        raise SourceError("podcast configuration must contain a feed list")
    if not isinstance(raw_feeds, list) or not 1 <= len(raw_feeds) <= 20:
        raise SourceError("podcast configuration must contain 1-20 feeds")

    feeds: List[Dict[str, Any]] = []
    for raw in raw_feeds:
        if isinstance(raw, str):
            feeds.append(
                {
                    "url": _feed_url(raw),
                    "name": "",
                    "category": "General Knowledge",
                    "max_episodes": default_limit,
                }
            )
            continue
        if not isinstance(raw, dict) or set(raw) - {
            "url",
            "name",
            "category",
            "max_episodes",
        }:
            raise SourceError("podcast feed contains unknown fields")
        url = _feed_url(raw.get("url"))
        feeds.append(
            {
                "url": url,
                "name": _label(raw.get("name"), name="feed name", default=""),
                "category": _label(
                    raw.get("category"),
                    name="feed category",
                    default="General Knowledge",
                ),
                "max_episodes": _episode_limit(raw.get("max_episodes", default_limit)),
            }
        )
    return feeds
