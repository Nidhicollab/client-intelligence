import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "client-industry-intel" / "skills" / "client-industry-intel"
sys.path.insert(0, str(SKILL / "scripts"))

import build_hub  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "sample-hub.json"
TEMPLATE = SKILL / "templates" / "hub.html"
DATA_OPEN = '<script id="hub-data" type="application/json">'


def sample():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def has_error(errors, text):
    return any(text in e for e in errors)


class ValidateTests(unittest.TestCase):
    def test_sample_is_valid(self):
        self.assertEqual(build_hub.validate(sample()), [])

    def test_rejects_unknown_role(self):
        d = sample()
        d["role"] = "sales"
        self.assertTrue(has_error(build_hub.validate(d), "role"))

    def test_requires_exactly_four_outputs(self):
        d = sample()
        d["outputs"] = d["outputs"][:3]
        self.assertTrue(has_error(build_hub.validate(d), "exactly 4"))

    def test_rejects_javascript_source_url(self):
        d = sample()
        d["records"][0]["source_url"] = "javascript:alert(1)"
        self.assertTrue(has_error(build_hub.validate(d), "source_url"))
        d = sample()
        d["miro_url"] = "javascript:alert(1)"
        self.assertTrue(has_error(build_hub.validate(d), "miro_url"))

    def test_client_document_must_be_confidential(self):
        d = sample()
        d["records"][3]["confidential"] = False
        self.assertTrue(has_error(build_hub.validate(d), "must be confidential"))

    def test_confidential_record_requires_confidential_hub(self):
        d = sample()
        d["confidential"] = False
        self.assertTrue(has_error(build_hub.validate(d), "confidential flag must be true"))

    def test_complete_output_needs_known_evidence(self):
        d = sample()
        d["outputs"][0]["evidence"] = ["r999"]
        self.assertTrue(has_error(build_hub.validate(d), "unknown record"))
        d = sample()
        d["outputs"][0]["evidence"] = []
        self.assertTrue(has_error(build_hub.validate(d), "at least one evidence"))

    def test_incomplete_output_needs_reason(self):
        d = sample()
        del d["outputs"][3]["reason"]
        self.assertTrue(has_error(build_hub.validate(d), "reason"))

    def test_table_rows_must_match_columns(self):
        d = sample()
        d["outputs"][1]["visual"]["rows"][0] = ["only one cell"]
        self.assertTrue(has_error(build_hub.validate(d), "must have 3 cells"))
        d = sample()
        d["outputs"][1]["visual"]["rows"][0][2] = {"text": "x", "level": "extreme"}
        self.assertTrue(has_error(build_hub.validate(d), "invalid level"))

    def test_rejects_reserved_or_bad_output_id(self):
        d = sample()
        d["outputs"][0]["id"] = "signals"
        self.assertTrue(has_error(build_hub.validate(d), "reserved"))
        d = sample()
        d["outputs"][0]["id"] = "Has Spaces"
        self.assertTrue(has_error(build_hub.validate(d), "lowercase"))

    def test_podcast_audio_must_be_local_file(self):
        d = sample()
        d["podcast"]["audio"] = "https://evil.example/a.mp3"
        self.assertTrue(has_error(build_hub.validate(d), "podcast.audio"))

    def test_rejects_unknown_visual_kind(self):
        d = sample()
        d["outputs"][0]["visual"] = {"kind": "image", "src": "x.png"}
        self.assertTrue(has_error(build_hub.validate(d), "visual.kind"))


class BuildTests(unittest.TestCase):
    def template(self):
        return TEMPLATE.read_text(encoding="utf-8")

    def embedded(self, html):
        return json.loads(html.split(DATA_OPEN, 1)[1].split("</script>", 1)[0])

    def test_build_injects_data_and_role_label(self):
        html = build_hub.build(sample(), self.template())
        self.assertNotIn(build_hub.PLACEHOLDER, html)
        data = self.embedded(html)
        self.assertEqual(data["company"], "Example Energy Co.")
        self.assertEqual(data["role_label"], "Product manager")

    def test_build_escapes_script_close(self):
        d = sample()
        evil = "</script><script>alert(1)</script><!-- x"
        d["records"][0]["claim"] = evil
        html = build_hub.build(d, self.template())
        self.assertNotIn("</script><script>alert(1)", html)
        self.assertEqual(self.embedded(html)["records"][0]["claim"], evil)

    def test_build_requires_placeholder(self):
        with self.assertRaises(ValueError):
            build_hub.build(sample(), "<html>no placeholder</html>")

    def test_template_never_uses_innerHTML(self):
        self.assertNotIn("innerHTML", self.template())
        self.assertNotIn("insertAdjacentHTML", self.template())
        self.assertNotIn("document.write", self.template())

    def test_template_pins_cdn_versions(self):
        t = self.template()
        self.assertIn("https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js", t)
        self.assertIn("https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js", t)
        self.assertIn('securityLevel: "strict"', t)

    def test_main_writes_file_and_rejects_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hub.html"
            self.assertEqual(build_hub.main([str(FIXTURE), str(out)]), 0)
            self.assertIn("Example Energy Co.", out.read_text(encoding="utf-8"))
            bad = Path(tmp) / "bad.json"
            d = sample()
            d["role"] = "sales"
            bad.write_text(json.dumps(d), encoding="utf-8")
            self.assertEqual(build_hub.main([str(bad), str(Path(tmp) / "bad.html")]), 1)
            self.assertFalse((Path(tmp) / "bad.html").exists())


if __name__ == "__main__":
    unittest.main()
