import contextlib
import io
import json
import unittest
from unittest.mock import patch

from public_podcast_summarizer.cli import main


class CliTests(unittest.TestCase):
    def test_config_run_logs_counts_only(self):
        item = {
            "podcast": "Private podcast selection",
            "title": "Secret-derived episode",
            "published": "today",
            "notes": "Publisher notes",
            "link": "https://example.test/episode",
            "review_status": "publisher_metadata_only",
        }
        episode = unittest.mock.Mock()
        episode.podcast = item["podcast"]
        episode.notes = item["notes"]
        episode.to_public_dict.return_value = dict(item)
        output = io.StringIO()
        feeds = [{"url": "https://example.test/feed.xml", "name": "Private name"}]

        with patch(
            "public_podcast_summarizer.cli.load_feeds_from_config", return_value=feeds
        ), patch("public_podcast_summarizer.cli.load_feed", return_value=b"<rss/>") , patch(
            "public_podcast_summarizer.cli.parse_feed", return_value=(episode,)
        ), patch(
            "public_podcast_summarizer.cli.summarize_notes", return_value=["summary"]
        ), patch(
            "public_podcast_summarizer.cli.send_digest", return_value=False
        ), contextlib.redirect_stdout(output):
            result = main(["--config", "--dry-run"])

        payload = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(
            payload,
            {"dry_run": True, "email_sent": False, "episode_count": 1, "feed_errors": 0},
        )
        self.assertNotIn(item["title"], output.getvalue())
        self.assertNotIn(feeds[0]["name"], output.getvalue())

    def test_mismatched_expected_channel_is_skipped_without_leaking_title(self):
        episode = unittest.mock.Mock()
        episode.podcast = "Unexpected Show"
        episode.notes = "Publisher notes"
        episode.to_public_dict.return_value = {
            "podcast": "Unexpected Show",
            "title": "Episode",
            "notes": "Publisher notes",
            "link": "https://example.test/episode",
        }
        output = io.StringIO()
        feeds = [
            {
                "url": "https://example.test/feed.xml",
                "expected_title": "Expected Show",
            }
        ]

        with patch(
            "public_podcast_summarizer.cli.load_feeds_from_config", return_value=feeds
        ), patch("public_podcast_summarizer.cli.load_feed", return_value=b"<rss/>"), patch(
            "public_podcast_summarizer.cli.parse_feed", return_value=(episode,)
        ), contextlib.redirect_stdout(output):
            with self.assertRaisesRegex(RuntimeError, "no configured feed yielded"):
                main(["--config", "--dry-run"])

        self.assertNotIn("Unexpected Show", output.getvalue())
        self.assertNotIn("Expected Show", output.getvalue())


if __name__ == "__main__":
    unittest.main()
