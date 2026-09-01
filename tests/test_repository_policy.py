import unittest
from pathlib import Path
import re


ROOT = Path(__file__).parents[1]


class RepositoryPolicyTests(unittest.TestCase):
    def test_workflow_is_minimal_pinned_and_secret_free(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("timeout-minutes: 5", workflow)
        self.assertIn("concurrency:", workflow)
        self.assertIn("actions/checkout@11d5960a326750d5838078e36cf38b85af677262", workflow)
        self.assertIn("actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("upload-artifact", workflow)
        self.assertNotIn("contents: write", workflow)

    def test_ci_is_event_driven_and_production_dispatch_is_safe_by_default(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        production = (ROOT / ".github/workflows/podcast-digest.yml").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("schedule:", ci)
        self.assertNotIn("secrets.", ci)
        self.assertIn("default: true", production)
        self.assertNotIn("pull_request:", production)
        self.assertNotIn("push:", production)
        self.assertNotIn("upload-artifact", production)
        self.assertEqual(production.count("cron:"), 1)
        self.assertNotIn(
            "    env:\n      PYTHONPATH: src\n      PODCAST_CONFIG_JSON:",
            production,
        )
        self.assertEqual(production.count("PODCAST_CONFIG_JSON:"), 1)
        self.assertLess(production.index("Run safety tests"), production.index("PODCAST_CONFIG_JSON:"))

    def test_public_tree_has_no_curated_subscription_defaults_or_pii(self):
        production = [ROOT / "README.md"]
        production += list((ROOT / "src").rglob("*.py"))
        production += list((ROOT / ".github/workflows").glob("*.yml"))
        source = (ROOT / "src/public_podcast_summarizer/source.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("DEFAULT_FEEDS", source)
        for path in production:
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertIsNone(
                re.search(r"[a-z0-9._%+-]+@(?!example\.test)[a-z0-9.-]+\.[a-z]{2,}", text, re.I),
                str(path.relative_to(ROOT)),
            )


if __name__ == "__main__":
    unittest.main()
