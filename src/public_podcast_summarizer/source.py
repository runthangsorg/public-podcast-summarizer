"""Load a bounded XML feed while explicitly refusing media downloads."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from typing import List, Dict, Any


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

DEFAULT_FEEDS: List[Dict[str, Any]] = [
    {"url": "https://feeds.megaphone.fm/hubermanlab", "name": "Huberman Lab", "category": "Health & Science", "max_episodes": 1},
    {"url": "https://lexfridman.com/feed/podcast/", "name": "Lex Fridman Podcast", "category": "AI & Deep Tech", "max_episodes": 1},
    {"url": "https://changelog.com/podcast/feed", "name": "The Changelog", "category": "Engineering & Open Source", "max_episodes": 1},
    {"url": "https://feeds.simplecast.com/_IjaDYAj", "name": "Deep Questions with Cal Newport", "category": "Focus & Productivity", "max_episodes": 1},
    {"url": "https://api.substack.com/feed/podcast/10845.rss", "name": "Lenny's Podcast", "category": "Product & Growth", "max_episodes": 1},
    {"url": "https://feeds.simplecast.com/Y8lFbOT4", "name": "Freakonomics Radio", "category": "Economics & Society", "max_episodes": 1},
    {"url": "https://feeds.redcircle.com/1796d08e-0a31-412d-b3fd-a14a489365ce", "name": "Blogging Theology", "category": "Philosophy & Thought", "max_episodes": 1},
    {"url": "https://api.substack.com/feed/podcast/1084089.rss", "name": "Latent Space AI", "category": "AI & Deep Tech", "max_episodes": 1},
]


def load_feeds_from_config() -> List[Dict[str, Any]]:
    """Parse PODCAST_CONFIG_JSON and return configured feeds with sensible defaults."""
    config_json = os.environ.get("PODCAST_CONFIG_JSON")
    if not config_json:
        return list(DEFAULT_FEEDS)
    
    try:
        config = json.loads(config_json)
        # Handle simple array of strings (backwards compatibility)
        if isinstance(config, list):
            if not config:
                return list(DEFAULT_FEEDS)
            return [{"url": str(item), "name": str(item)} for item in config]
        
        # Handle dict format: {"feeds": [{"url": "...", "name": "..."}], "max_episodes": 5}
        if isinstance(config, dict):
            feeds = config.get("feeds", [])
            if not feeds:
                return list(DEFAULT_FEEDS)
            max_episodes = config.get("max_episodes", 1)
            for feed in feeds:
                if "max_episodes" not in feed:
                    feed["max_episodes"] = max_episodes
            return feeds
            
        return list(DEFAULT_FEEDS)
    except json.JSONDecodeError:
        return list(DEFAULT_FEEDS)
