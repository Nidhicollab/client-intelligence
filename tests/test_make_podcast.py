import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "client-industry-intel" / "skills" / "client-industry-intel"
sys.path.insert(0, str(SKILL / "scripts"))

import make_podcast as mp  # noqa: E402


def script_text(words_per_host=1100):
    return (
        "# Example Energy podcast\n\n"
        "HOST A: " + "grid " * words_per_host + "\n"
        "**HOST B:** " + "outage " * words_per_host + "\n"
    )


class ParseTests(unittest.TestCase):
    def test_parses_speakers_continuations_and_strips_directions(self):
        text = (
            "# Title\n\nIntro line with no speaker.\n"
            "HOST A: Hello there.\nThis continues.\n"
            "**HOST B:** Hi. [laughs]\n\n"
            "NARRATOR: Done."
        )
        self.assertEqual(
            mp.parse_script(text),
            [("HOST A", "Hello there. This continues."), ("HOST B", "Hi."), ("NARRATOR", "Done.")],
        )

    def test_accepts_bold_before_colon(self):
        self.assertEqual(mp.parse_script("**HOST A**: Hi."), [("HOST A", "Hi.")])

    def test_estimate_minutes(self):
        words, minutes = mp.estimate_minutes([("HOST A", "word " * 300)])
        self.assertEqual((words, minutes), (300, 2.0))


class ChunkTests(unittest.TestCase):
    def test_chunks_respect_limit_and_keep_all_words(self):
        text = " ".join(f"Sentence number {i} is here." for i in range(200))
        chunks = mp.chunk_text(text, 300)
        self.assertTrue(all(len(c) <= 300 for c in chunks))
        self.assertEqual(" ".join(chunks).split(), text.split())

    def test_splits_a_sentence_longer_than_the_limit(self):
        text = "word " * 100
        chunks = mp.chunk_text(text, 50)
        self.assertTrue(all(len(c) <= 50 for c in chunks))
        self.assertEqual(" ".join(chunks).split(), text.split())


class ChooseModeTests(unittest.TestCase):
    def test_auto_prefers_openai_then_elevenlabs_then_mac(self):
        self.assertEqual(mp.choose_mode("auto", {"OPENAI_API_KEY": "k"}, "darwin")[0], "openai")
        self.assertEqual(mp.choose_mode("auto", {"ELEVENLABS_API_KEY": "k"}, "darwin")[0], "elevenlabs")
        self.assertEqual(mp.choose_mode("auto", {}, "darwin"), ("mac", ""))

    def test_auto_without_mac_or_key_is_script_only(self):
        mode, note = mp.choose_mode("auto", {}, "linux")
        self.assertEqual(mode, "script")
        self.assertIn("script", note)

    def test_requested_service_without_key_falls_back(self):
        mode, note = mp.choose_mode("openai", {}, "darwin")
        self.assertEqual(mode, "mac")
        self.assertIn("OPENAI_API_KEY", note)

    def test_mac_on_other_platforms_is_script_only(self):
        self.assertEqual(mp.choose_mode("mac", {}, "win32")[0], "script")


class MakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.script = self.dir / "podcast-script.md"
        self.script.write_text(script_text(), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_openai_uses_two_voices_and_writes_mp3(self):
        calls = []

        def fake_post(url, headers, body):
            calls.append((url, headers, body))
            return b"MP3"

        result = mp.make(self.script, self.dir, "openai", {"OPENAI_API_KEY": "sk-test"}, "darwin", post=fake_post)
        self.assertEqual(result["mode"], "openai")
        self.assertEqual(result["audio"], "podcast.mp3")
        self.assertEqual((self.dir / "podcast.mp3").read_bytes(), b"MP3" * len(calls))
        voices = {body["voice"] for _, _, body in calls}
        self.assertEqual(voices, {"alloy", "nova"})
        self.assertTrue(all(h["Authorization"] == "Bearer sk-test" for _, h, _ in calls))
        self.assertTrue(all(len(b["input"]) <= mp.OPENAI_CHAR_LIMIT for _, _, b in calls))
        self.assertTrue(all(b["model"] == mp.OPENAI_MODEL for _, _, b in calls))

    def test_elevenlabs_sends_key_header(self):
        calls = []

        def fake_post(url, headers, body):
            calls.append((url, headers, body))
            return b"MP3"

        result = mp.make(self.script, self.dir, "elevenlabs", {"ELEVENLABS_API_KEY": "el-test"}, "darwin", post=fake_post)
        self.assertEqual(result["mode"], "elevenlabs")
        self.assertTrue(all(h["xi-api-key"] == "el-test" for _, h, _ in calls))
        self.assertTrue(all(url.startswith("https://api.elevenlabs.io/") for url, _, _ in calls))

    def test_service_failure_falls_back_to_mac(self):
        commands = []

        def failing_post(url, headers, body):
            raise OSError("connection reset")

        def fake_run(cmd, check):
            commands.append(cmd[0])

        result = mp.make(self.script, self.dir, "openai", {"OPENAI_API_KEY": "k"}, "darwin", run=fake_run, post=failing_post)
        self.assertEqual(result["mode"], "mac")
        self.assertEqual(result["audio"], "podcast.m4a")
        self.assertEqual(commands, ["say", "afconvert"])
        self.assertTrue(any("failed" in n for n in result["notes"]))

    def test_dropped_download_falls_back_to_mac(self):
        import http.client

        def dropping_post(url, headers, body):
            raise http.client.IncompleteRead(b"partial")

        result = mp.make(self.script, self.dir, "openai", {"OPENAI_API_KEY": "k"}, "darwin",
                         run=lambda cmd, check: None, post=dropping_post)
        self.assertEqual((result["mode"], result["audio"]), ("mac", "podcast.m4a"))
        self.assertTrue(any("failed" in n for n in result["notes"]))

    def test_bad_request_value_falls_back_to_script_off_mac(self):
        def bad_post(url, headers, body):
            raise ValueError("URL can't contain control characters")

        result = mp.make(self.script, self.dir, "elevenlabs", {"ELEVENLABS_API_KEY": "k"}, "linux", post=bad_post)
        self.assertEqual((result["mode"], result["audio"]), ("script", None))

    def test_mac_mode_runs_say_then_afconvert(self):
        commands = []

        def fake_run(cmd, check):
            commands.append(cmd)

        result = mp.make(self.script, self.dir, "mac", {}, "darwin", run=fake_run)
        self.assertEqual([c[0] for c in commands], ["say", "afconvert"])
        self.assertIn("-v", commands[0])
        self.assertEqual(result["audio"], "podcast.m4a")

    def test_mac_mode_estimates_at_mac_speaking_rate(self):
        result = mp.make(self.script, self.dir, "mac", {}, "darwin", run=lambda cmd, check: None)
        self.assertEqual(result["minutes"], round(2200 / mp.MAC_WORDS_PER_MINUTE, 1))
        self.assertTrue(any("target is 13 to 17" in n for n in result["notes"]))

    def test_mac_failure_leaves_script_only(self):
        def failing_run(cmd, check):
            raise OSError("say not found")

        result = mp.make(self.script, self.dir, "mac", {}, "darwin", run=failing_run)
        self.assertEqual((result["mode"], result["audio"]), ("script", None))

    def test_script_only_on_linux_without_key(self):
        result = mp.make(self.script, self.dir, "auto", {}, "linux")
        self.assertEqual((result["mode"], result["audio"]), ("script", None))

    def test_reports_length_outside_target(self):
        self.script.write_text(script_text(words_per_host=150), encoding="utf-8")
        result = mp.make(self.script, self.dir, "script", {}, "darwin")
        self.assertTrue(any("target is 13 to 17" in n for n in result["notes"]))

    def test_no_speaker_lines_is_an_error(self):
        self.script.write_text("Just prose with no speakers.", encoding="utf-8")
        with self.assertRaises(ValueError):
            mp.make(self.script, self.dir, "script", {}, "darwin")

    def test_cli_prints_json(self):
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = mp.main(["--script", str(self.script), "--out-dir", str(self.dir), "--mode", "script"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buf.getvalue())["mode"], "script")


if __name__ == "__main__":
    unittest.main()
