import contextlib
import io
import os
import unittest
from unittest.mock import patch

from public_podcast_summarizer.mailer import MailConfigError, send_digest


class MailerTests(unittest.TestCase):
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
