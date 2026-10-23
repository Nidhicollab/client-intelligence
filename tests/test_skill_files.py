import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "client-industry-intel" / "skills" / "client-industry-intel"
ROLE_SLUGS = ["product-manager", "engineering-lead", "ux-designer", "engagement-lead", "data-analyst"]
VISUAL_KINDS = {"mermaid", "chart", "cards", "table"}


class RoleFileTests(unittest.TestCase):
    def test_each_role_file_has_required_sections(self):
        for slug in ROLE_SLUGS:
            with self.subTest(role=slug):
                text = (SKILL / "roles" / f"{slug}.md").read_text(encoding="utf-8")
                for heading in ("## Research asks", "## Outputs", "## Podcast segment"):
                    self.assertIn(heading, text)
                self.assertEqual(len(re.findall(r"^### [2-5]\. ", text, re.M)), 4)
                kinds = re.findall(r"^\*\*Visual:\*\* `(\w+)`", text, re.M)
                self.assertEqual(len(kinds), 4)
                self.assertTrue(set(kinds) <= VISUAL_KINDS, kinds)


class PrivacyTests(unittest.TestCase):
    def test_no_email_addresses_in_plugin(self):
        pattern = re.compile(r"[\w.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")
        for path in (ROOT / "plugins").rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".py", ".html"}:
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertIsNone(pattern.search(path.read_text(encoding="utf-8")))


class OutputGuideTests(unittest.TestCase):
    def read(self, name):
        return (SKILL / "outputs" / name).read_text(encoding="utf-8")

    def test_podcast_guide_uses_script_and_formats(self):
        text = self.read("podcast.md")
        self.assertIn("scripts/make_podcast.py", text)
        for marker in ("HOST A:", "HOST B:", "NARRATOR:", "2,200"):
            self.assertIn(marker, text)

    def test_hub_guide_documents_schema_and_builder(self):
        text = self.read("hub.md")
        self.assertIn("scripts/build_hub.py", text)
        for key in ("company", "as_of", "role", "confidential", "miro_url", "podcast", "outputs", "signals", "records"):
            self.assertIn(f"`{key}`", text)

    def test_miro_guide_exists(self):
        self.assertIn("miro_url", self.read("miro.md"))


class NewsletterGuideTests(unittest.TestCase):
    def test_newsletter_guide_covers_delivery_and_limits(self):
        text = (SKILL / "outputs" / "newsletter.md").read_text(encoding="utf-8")
        for phrase in ("last 24 hours", "Gmail", "Slack", "official careers page", "never include", "Daily task prompt"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
