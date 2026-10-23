# Podcast

Every user gets this output first. It is a spoken briefing of about 15 minutes.

## 1. Write the script

Write `clients/<company-slug>/podcast-script.md`.

- Length for a text-to-speech service: about 2,200 words (13 to 17 minutes at 150 words per minute).
- Length for the Mac voice: about 2,700 words, because the Mac voice speaks faster, at about 180 words per minute. Scale each part's word budget below by the same amount.
- Mac voice: every line starts with `NARRATOR:`, because the Mac voice reads one voice.
- Text-to-speech service: two hosts in conversation. Lines start with `HOST A:` or `HOST B:`. Host A leads; Host B asks the questions the listener would ask and pushes back.
- A `#` title line at the top is fine. Anything in `[square brackets]` is not spoken.

Running order and word budget:

| Part | Words | Content |
|---|---|---|
| Cold open | 100 | The single most surprising finding, as a hook |
| The company in two minutes | 300 | What it does, how it makes money, latest results |
| Industry and competitors | 500 | Where the industry is going; incumbent, adjacent and insurgent threats |
| For your role | 400 | The `## Podcast segment` from the role file |
| Risks and signals | 500 | SPEED-C headwinds, what hiring and news say right now |
| What to do this week | 400 | 3 concrete actions and the questions to raise with the client |

Style rules:

- Write for the ear: short sentences, no tables, no URLs.
- Name sources in speech: "according to their second-quarter 10-Q", "an analyst note from September".
- Say aloud when something is an estimate or inference.
- Round numbers for speech and keep the unit: "about 4.2 billion dollars".
- If an SOW was used, details from it may appear, and the podcast is then confidential.

## 2. Make the audio

Run, with the mode the user chose in Step 3 (`mac`, `openai` or `elevenlabs`; `auto` if they did not choose):

```bash
python3 "<skill folder>/scripts/make_podcast.py" --script "clients/<company-slug>/podcast-script.md" --out-dir "clients/<company-slug>" --mode <mode>
```

The script prints JSON: `mode`, `audio` (file name or null), `words`, `minutes`, `notes`.

- If `notes` says the script is outside 13 to 17 minutes, revise the script toward 2,200 words and run again, once.
- If `audio` is null, the script is the deliverable; tell the user why, using `notes`.

## 3. Record it in the hub data

Copy the result into `hub.json`:

```json
"podcast": {"audio": "<audio>", "script": "podcast-script.md", "voice": "<mode>", "minutes": <minutes>, "notes": [<notes>]}
```
