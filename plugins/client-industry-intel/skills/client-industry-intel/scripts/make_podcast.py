#!/usr/bin/env python3
"""Turn a podcast script into audio with the Mac voice or a text-to-speech service.

Usage: python3 make_podcast.py --script podcast-script.md --out-dir DIR --mode auto
Speaker lines start with HOST A:, HOST B: or NARRATOR:. Prints a JSON result.
"""
import argparse
import http.client
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

WORDS_PER_MINUTE = 150
# The Mac voice ignores slower rates and speaks about 180 words a minute (measured).
MAC_WORDS_PER_MINUTE = 180
TARGET_MINUTES = (13, 17)
SPEAKER_RE = re.compile(r"^\**\s*(HOST A|HOST B|NARRATOR)\s*\**\s*:\s*\**\s*(.*)$")
DIRECTION_RE = re.compile(r"\[[^\]]*\]")

MAC_VOICE = "Samantha"

OPENAI_URL = "https://api.openai.com/v1/audio/speech"
OPENAI_MODEL = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_VOICES = {"HOST A": "alloy", "HOST B": "nova", "NARRATOR": "alloy"}
OPENAI_CHAR_LIMIT = 4096

ELEVEN_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
ELEVEN_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVEN_VOICES = {
    "HOST A": os.environ.get("ELEVENLABS_VOICE_A", "21m00Tcm4TlvDq8ikWAM"),
    "HOST B": os.environ.get("ELEVENLABS_VOICE_B", "pNInz6obpgDQGcFmaJgB"),
}
ELEVEN_VOICES["NARRATOR"] = ELEVEN_VOICES["HOST A"]
ELEVEN_CHAR_LIMIT = 5000


def parse_script(text):
    """Return (speaker, text) pairs from a script. Lines before the first speaker are ignored."""
    segments = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = SPEAKER_RE.match(stripped)
        if match:
            segments.append([match.group(1), match.group(2)])
        elif segments:
            segments[-1][1] += " " + stripped
    cleaned = []
    for speaker, words in segments:
        words = re.sub(r"\s+", " ", DIRECTION_RE.sub("", words)).strip()
        if words:
            cleaned.append((speaker, words))
    return cleaned


def estimate_minutes(segments, words_per_minute=WORDS_PER_MINUTE):
    words = sum(len(text.split()) for _, text in segments)
    return words, round(words / words_per_minute, 1)


def chunk_text(text, limit):
    """Split text into pieces of at most `limit` characters, breaking at sentences, then spaces."""
    chunks, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        while len(sentence) > limit:
            cut = sentence.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            if current:
                chunks.append(current)
                current = ""
            chunks.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if not sentence:
            continue
        if current and len(current) + 1 + len(sentence) > limit:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks


def choose_mode(requested, env, platform):
    """Pick the voice mode. Returns (mode, note); the note explains any fallback."""
    is_mac = platform == "darwin"
    fallback = "mac" if is_mac else "script"
    fallback_text = "used the Mac voice." if is_mac else "saved the script only."
    if requested == "auto":
        if env.get("OPENAI_API_KEY"):
            return "openai", ""
        if env.get("ELEVENLABS_API_KEY"):
            return "elevenlabs", ""
        if is_mac:
            return "mac", ""
        return "script", "No Mac voice and no text-to-speech key, so only the script was saved."
    if requested == "openai" and not env.get("OPENAI_API_KEY"):
        return fallback, "OPENAI_API_KEY is not set; " + fallback_text
    if requested == "elevenlabs" and not env.get("ELEVENLABS_API_KEY"):
        return fallback, "ELEVENLABS_API_KEY is not set; " + fallback_text
    if requested == "mac" and not is_mac:
        return "script", "The Mac voice needs macOS; saved the script only."
    return requested, ""


def _post(url, headers, body):
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def synth_service(mode, segments, env, out_dir, post=_post):
    parts = []
    limit = OPENAI_CHAR_LIMIT if mode == "openai" else ELEVEN_CHAR_LIMIT
    for speaker, text in segments:
        for chunk in chunk_text(text, limit):
            if mode == "openai":
                parts.append(post(
                    OPENAI_URL,
                    {"Authorization": f"Bearer {env['OPENAI_API_KEY']}"},
                    {"model": OPENAI_MODEL, "voice": OPENAI_VOICES[speaker], "input": chunk, "response_format": "mp3"},
                ))
            else:
                parts.append(post(
                    ELEVEN_URL.format(voice=ELEVEN_VOICES[speaker]),
                    {"xi-api-key": env["ELEVENLABS_API_KEY"]},
                    {"text": chunk, "model_id": ELEVEN_MODEL},
                ))
    out = Path(out_dir) / "podcast.mp3"
    out.write_bytes(b"".join(parts))
    return out


def synth_mac(segments, out_dir, run=subprocess.run):
    out = Path(out_dir) / "podcast.m4a"
    with tempfile.TemporaryDirectory() as tmp:
        text_file = Path(tmp) / "script.txt"
        aiff = Path(tmp) / "podcast.aiff"
        text_file.write_text("\n\n".join(text for _, text in segments), encoding="utf-8")
        run(["say", "-v", MAC_VOICE, "-f", str(text_file), "-o", str(aiff)], check=True)
        run(["afconvert", "-f", "m4af", "-d", "aac", str(aiff), str(out)], check=True)
    return out


def make(script_path, out_dir, requested="auto", env=None, platform=None, run=subprocess.run, post=_post):
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    segments = parse_script(Path(script_path).read_text(encoding="utf-8"))
    if not segments:
        raise ValueError("no speaker lines found; lines must start with HOST A:, HOST B: or NARRATOR:")
    notes = []
    mode, note = choose_mode(requested, env, platform)
    if note:
        notes.append(note)

    audio = None
    if mode in ("openai", "elevenlabs"):
        try:
            audio = synth_service(mode, segments, env, out_dir, post)
        except (OSError, http.client.HTTPException, ValueError) as exc:
            mode = "mac" if platform == "darwin" else "script"
            notes.append(
                f"The text-to-speech service failed ({exc}); "
                + ("used the Mac voice." if mode == "mac" else "saved the script only.")
            )
    if mode == "mac":
        try:
            audio = synth_mac(segments, out_dir, run)
        except (OSError, subprocess.CalledProcessError) as exc:
            notes.append(f"The Mac voice failed ({exc}); saved the script only.")
            audio = None
    final_mode = mode if audio else "script"
    words, minutes = estimate_minutes(segments, MAC_WORDS_PER_MINUTE if final_mode == "mac" else WORDS_PER_MINUTE)
    low, high = TARGET_MINUTES
    if not low <= minutes <= high:
        notes.insert(0, f"Script runs about {minutes} minutes; the target is {low} to {high}.")
    return {
        "mode": final_mode,
        "audio": audio.name if audio else None,
        "words": words,
        "minutes": minutes,
        "notes": notes,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Turn a podcast script into audio.")
    parser.add_argument("--script", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--mode", choices=["auto", "mac", "openai", "elevenlabs", "script"], default="auto")
    args = parser.parse_args(argv)
    try:
        result = make(args.script, args.out_dir, args.mode)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
