import contextlib
import io
import os
import unittest
from unittest.mock import patch

from public_podcast_summarizer.mailer import (
    MailConfigError,
    _build_html,
    _display_date,
    send_digest,
)


class MailerTests(unittest.TestCase):
    def test_publisher_timestamp_is_rendered_as_a_readable_date(self):
        self.assertEqual(
            _display_date("Thu, 27 Aug 2026 08:00:00 -0000"),
            "27 Aug 2026",
        )
        self.assertEqual(
            _display_date("2026-08-26T15:15:00+00:00"),
            "26 Aug 2026",
        )

    def test_show_page_fallback_is_truthfully_labelled(self):
        rendered = _build_html(
            [
                {
                    "podcast_name": "Example Show",
                    "title": "Episode",
                    "link": "https://example.test/show",
                    "link_kind": "show_page",
                    "summary": ["Publisher notes."],
                }
            ]
        )

        self.assertIn("Open Publisher Show", rendered)
        self.assertNotIn("Listen / View Episode", rendered)

    def test_dry_run_never_prints_recipient_or_secret_derived_digest(self):
        output = io.StringIO()
        items = [
            {
                "podcast_name": "Private podcast selection",
                "title": "A private-interest episode",
                "link": "https://example.test/episode",
                "summary": ["Private-interest publisher notes."],
            }
        ]
        with patch.dict(
            os.environ,
            {"REPORT_RECIPIENT": "private@example.test"},
            clear=True,
        ), contextlib.redirect_stdout(output):
            sent = send_digest(items, dry_run=True)

        self.assertFalse(sent)
        self.assertEqual(output.getvalue(), "")

    def test_live_delivery_fails_closed_when_credentials_are_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(MailConfigError):
                send_digest([], dry_run=False)


if __name__ == "__main__":
    unittest.main()
