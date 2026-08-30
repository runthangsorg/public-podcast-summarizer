import tempfile
import unittest
from pathlib import Path

from public_podcast_summarizer.source import SourceError, load_feed


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


if __name__ == "__main__":
    unittest.main()
