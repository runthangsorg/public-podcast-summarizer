import unittest

from public_podcast_summarizer.summary import summarize_notes


class SummaryTests(unittest.TestCase):
    def test_summary_is_deterministic_and_bounded(self):
        notes = (
            "First, bounded queues protect services during traffic spikes. "
            "Second, backpressure gives callers an explicit retry signal. "
            "Third, dashboards should report dropped work. "
            "Fourth, this sentence should not appear."
        )

        summary = summarize_notes(notes, max_points=3, max_chars=180)

        self.assertEqual(len(summary), 3)
        self.assertTrue(all(len(point) <= 180 for point in summary))
        self.assertNotIn("Fourth", " ".join(summary))

    def test_empty_notes_are_explicit(self):
        self.assertEqual(summarize_notes(""), ["No publisher notes were provided."])


if __name__ == "__main__":
    unittest.main()
