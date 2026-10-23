# Hub

The hub is one HTML file, `clients/<company-slug>/hub.html`, built from `clients/<company-slug>/hub.json` by a script. Never write the HTML by hand.

## 1. Write `hub.json`

Top-level keys:

| Key | Value |
|---|---|
| `company` | The confirmed company name |
| `as_of` | Today's date, `YYYY-MM-DD` |
| `role` | `product-manager`, `engineering-lead`, `ux-designer`, `engagement-lead` or `data-analyst` |
| `confidential` | `true` if an SOW or proposal was used, else `false` |
| `miro_url` | The Miro board link, or `null` |
| `notes` | Short strings shown under the title: skipped options, assumptions, failures |
| `podcast` | From `outputs/podcast.md` step 3 |
| `outputs` | Exactly four objects, for outputs 2 to 5 in the role file's order |
| `signals` | The Signals agent's object, as saved in `signals.json` |
| `records` | Every verified evidence record, each with its `id` |

Each object in `outputs`:

```json
{
  "id": "opportunity-tree",
  "title": "Opportunity tree",
  "status": "complete",
  "so_what": "Two or three sentences on what this means for the engagement.",
  "visual": {"kind": "mermaid", "code": "flowchart TD\n  A[Outcome] --> B[Problem]"},
  "caption": "Optional: what is inferred, what the SOW contributed.",
  "evidence": ["r001", "r007"]
}
```

- `id`: lowercase words joined by hyphens. Not `podcast`, `signals` or `sources`.
- `visual.kind` and its fields:
  - `mermaid`: `code`, the Mermaid source. Keep node labels short. Quote labels that contain brackets or colons.
  - `chart`: `config`, a Chart.js 4 configuration object.
  - `cards`: `cards`, a list of `{"title", "subtitle", "body": [lines], "tags": [strings]}`.
  - `table`: `columns` (list of headers) and `rows` (lists the same length as `columns`). A cell can be `{"text": "High", "level": "high"}` to color it; levels are `high`, `medium`, `low`.
- `evidence`: the ids of the records behind the output. At least one.
- If the research for an output did not finish, use `{"id", "title", "status": "incomplete", "reason": "..."}` and nothing else. Never fill it with guesses.

Records: the evidence records from Step 6, unchanged. Records from client documents keep `evidence_type: "client_document"`, `confidential: true`, and the file name as `source_url`.

## 2. Build and check

```bash
python3 "<skill folder>/scripts/build_hub.py" "clients/<company-slug>/hub.json" "clients/<company-slug>/hub.html"
```

If it prints errors, fix `hub.json` and run it again. Do not hand-edit `hub.html`.

Then open the file so the user sees it: `open "clients/<company-slug>/hub.html"` on macOS.

Diagrams and charts load from the internet, so tell the user the hub needs a connection to draw them.
