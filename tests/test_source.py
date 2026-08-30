import tempfile
import unittest
from pathlib import Path

from public_podcast_summarizer.source import (
    SourceError,
    load_feed,
    load_feeds_from_config,
)


class SourceTests(unittest.TestCase):
    def test_loads_bounded_local_feed(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "feed.xml"
            source.write_bytes(b"<rss/>")
            self.assertEqual(load_feed(str(source)), b"<rss/>")

    def test_rejects_audio_and_unknown_url_schemes(self):
        for source in (
            "ftp://example.test/feed.xml",
            "file:///private/feed.xml",
            "https://example.test/audio.mp3",
        ):
            with self.subTest(source=source), self.assertRaises(SourceError):
                load_feed(source)

    def test_runtime_feed_config_is_required_and_strict(self):
        for payload in (None, "", "not json", "[]", '{"feeds": []}'):
            with self.subTest(payload=payload), self.assertRaises(SourceError):
                load_feeds_from_config(payload)

    def test_runtime_feed_config_is_bounded_and_copied(self):
        feeds = load_feeds_from_config(
            '{"max_episodes": 2, "feeds": ['
            '{"url": "https://example.test/feed.xml", "name": "Example", '
            '"category": "Engineering"}]}'
        )

        self.assertEqual(
            feeds,
            [
                {
                    "url": "https://example.test/feed.xml",
                    "name": "Example",
                    "category": "Engineering",
                    "max_episodes": 2,
                }
            ],
        )

    def test_runtime_feed_config_rejects_media_and_unknown_fields(self):
        for payload in (
            '{"feeds": [{"url": "https://example.test/audio.mp3"}]}',
            '{"feeds": [{"url": "file:///private/feed.xml"}]}',
            '{"feeds": [{"url": "https://example.test/feed.xml", "token": "x"}]}',
        ):
            with self.subTest(payload=payload), self.assertRaises(SourceError):
                load_feeds_from_config(payload)


if __name__ == "__main__":
    unittest.main()
