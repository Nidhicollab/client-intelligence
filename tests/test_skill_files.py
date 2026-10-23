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


class SkillFileTests(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter_name(self):
        self.assertTrue(self.text.startswith('---\nname: "client-industry-intel"\n'))

    def test_referenced_files_exist(self):
        paths = set(re.findall(r"`((?:roles|outputs|templates|scripts)/[\w.-]+\.(?:md|py|html))`", self.text))
        self.assertGreaterEqual(len(paths), 7)
        for rel in paths:
            with self.subTest(path=rel):
                self.assertTrue((SKILL / rel).is_file())

    def test_lists_every_role_slug(self):
        for slug in ROLE_SLUGS:
            self.assertIn(f"`{slug}`", self.text)

    def test_has_nine_steps_and_seven_agents(self):
        for n in range(1, 10):
            self.assertIn(f"## Step {n}:", self.text)
        self.assertIn("7. **Signals.**", self.text)

    def test_keeps_v1_frameworks(self):
        for phrase in ("Incumbent", "Adjacent", "Insurgent", "SPEED-C", "KPI"):
            self.assertIn(phrase, self.text)


import json  # noqa: E402


class ReleaseTests(unittest.TestCase):
    def test_plugin_version(self):
        meta = json.loads((ROOT / "plugins/client-industry-intel/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["version"], "2.0.0")

    def test_readme_covers_v2(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in ("Product manager", "Engineering lead", "UX or product designer", "Engagement lead", "data analyst",
                       "podcast", "newsletter", "Signals", "Miro", "website URL"):
            self.assertIn(phrase, text)


class ReviewFixTests(unittest.TestCase):
    def test_skill_gives_signals_agent_the_hub_shape(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for key in ('"dimension"', '"notable_roles"', '"careers_url"', '"board_url"', '"paywalled"'):
            self.assertIn(key, text)

    def test_podcast_guide_covers_timeout_mode_and_confidentiality(self):
        text = (SKILL / "outputs" / "podcast.md").read_text(encoding="utf-8")
        self.assertIn("600000", text)
        self.assertIn("the `mode` field", text)
        self.assertIn("leaves the machine", text)

    def test_voice_question_maps_to_auto(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`--mode auto`", text)


if __name__ == "__main__":
    unittest.main()
