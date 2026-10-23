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


if __name__ == "__main__":
    unittest.main()
