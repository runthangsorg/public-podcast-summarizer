"""Load a bounded XML feed while explicitly refusing media downloads."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class SourceError(ValueError):
    """Raised when a feed source is unsafe, too large, or unavailable."""


def load_feed(
    source: str, *, timeout: int = 15, max_bytes: int = 2_000_000
) -> bytes:
    parts = urlsplit(source)
    try:
        if parts.scheme:
            if parts.scheme not in {"http", "https"} or not parts.netloc:
                raise SourceError("only HTTP(S) feed URLs are supported")
            if parts.path.lower().endswith((".mp3", ".m4a", ".wav", ".mp4")):
                raise SourceError("media downloads are not supported")
            request = Request(source, headers={"User-Agent": "public-podcast-summarizer/1"})
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
