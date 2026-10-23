---
name: "client-industry-intel"
description: "Start from a company's website URL and build a fact-checked client and industry hub tailored to the user's role: a 15-minute podcast plus four visual outputs, an optional Miro board, and a daily newsletter. Runs parallel research agents."
---

# Client & Industry Intelligence Hub

Purpose: when someone starts work with a new client, turn the company's website URL and their project context into a fact-checked hub built for their role: a 15-minute podcast and four visuals. Every claim must trace to a source. Gaps are stated as gaps and never filled with plausible numbers.

The reasoning style is a consulting transformation analysis: market pressures, then incumbent, adjacent and insurgent competitors, then capability gaps and actions. Quantify where sources allow, and say explicitly when something is inferred rather than disclosed.

## Supporting files

Paths are relative to this skill's folder. Open a file only when its step runs. Run scripts by their full path: `python3 "<skill folder>/scripts/<name>.py"`.

| File | Open at |
|---|---|
| `roles/product-manager.md`, `roles/engineering-lead.md`, `roles/ux-designer.md`, `roles/engagement-lead.md`, `roles/data-analyst.md` | Step 3: read the one matching the user's role |
| `outputs/podcast.md` | Step 7 |
| `outputs/hub.md` | Step 7 |
| `outputs/miro.md` | Step 7, only if the user wants a Miro board |
| `outputs/newsletter.md` | Step 9 |
| `scripts/make_podcast.py` | Step 7, as `outputs/podcast.md` describes |
| `scripts/build_hub.py` | Step 7, as `outputs/hub.md` describes |
| `templates/hub.html` | Used by `scripts/build_hub.py`. Never edit it during a run. |

Roles:

| # | Role | Slug |
|---|---|---|
| 1 | Product manager | `product-manager` |
| 2 | Engineering lead or architect | `engineering-lead` |
| 3 | UX or product designer | `ux-designer` |
| 4 | Engagement lead or partner | `engagement-lead` |
| 5 | Business or data analyst | `data-analyst` |

## Step 1: Get the URL

If the request has no company website URL, ask for one. Then read the site's key pages: about, products, investor relations, newsroom, leadership and careers. Work out:

- the company name and legal entity
- public, private or subsidiary; for a subsidiary, the parent that files reports
- industry, geography, segments and main products
- the official careers page URL, and the job board behind it if the careers page sends applicants to one (Greenhouse, Lever, Workday or similar)

If the site blocks automated reading, ask for the company name and continue from that.

## Step 2: Confirm the company

Check each item from Step 1 against an independent source: a filing, a regulator, or major business press. Show a short summary with each item marked confirmed or unconfirmed, and its source. If the parent and subsidiary are unclear, ask which one the engagement is with. Wait for the user to confirm or correct before any research starts.

## Step 3: About you

Send one plain message asking for:

1. Their role, by number from the roles table above. Map any other role to the closest one and say which.
2. 2 or 3 lines on what they have been asked to build or change.
3. The project or idea focus.
4. Optionally, file paths for the client's proposal and SOW. They can drag the files into the prompt.

Then, in one AskUserQuestion call:

- **Podcast voice:** "Mac voice" (built in, one narrator, run with `--mode mac`), and "Text-to-speech service" (two hosts, run with `--mode auto`) only if `OPENAI_API_KEY` or `ELEVENLABS_API_KEY` is set (check with `printenv OPENAI_API_KEY ELEVENLABS_API_KEY | wc -l`, never print the keys). If the machine is not a Mac and no key is set, skip this question and tell the user the podcast will be a script only.
- **Miro board:** yes or no. Ask only if the Miro connector's tools are available.

Read the role's file from `roles/` now.

Every run is full depth. The investor view runs for public companies only. The funding radar always runs.

## Step 4: Read the client documents

If the user gave a proposal or SOW, read them here. Extract scope and deliverables, timeline, named stakeholders and success criteria. If a file is a scanned PDF you cannot read, ask for a text version or continue without it.

Confidentiality:

- Never put client document content in a web search query.
- Write a short **scope summary** for the agents: the kind of work and the business areas it touches, with no names of client staff, no figures and no contract terms.
- Every record taken from a client document has `evidence_type: "client_document"` and `confidential: true`.

## Step 5: Research with seven agents in parallel

Spawn all seven agents with the Agent tool in a single message so they run in parallel. Use subagent_type general-purpose. Pass each one: the confirmed company profile from Step 2, the role, the user's task and focus, the scope summary, its assignment below plus that agent's research asks from the role file, the shared rules, and the output schema. Skip agent 2 for companies that are not public.

**Shared rules for every agent:**

- Search the web. Prefer sources from the last 12 months, and mark anything older.
- Source priority, from highest to lowest: regulatory filings and regulators (10-K, 10-Q, 8-K, FERC, state PUCs, EIA, SEC), earnings materials and call transcripts, company releases and website, reputable research and industry bodies, major business press, and trade press. Blogs and forums count only as sentiment and must be labeled that way.
- A claim found only on the company's own website is a company claim. Look for an independent source; if there is none, say so.
- Label every metric with its value, unit, reporting period and reporting entity.
- Keep reported facts, analyst or third-party estimates, and your own interpretation separate.
- If data isn't public, return a record with the claim "not publicly available" and name the closest proxy.
- Agents 1 to 6 return between 10 and 25 records. Agent 7 returns one object in its own shape, below.

**Output schema.** Agents 1 to 6 return a JSON array of records in this shape:

```json
{
  "section": "company|financials|investor|industry|funding|customers|competitors|speedc",
  "claim": "concise, checkable finding",
  "entity": "who it concerns",
  "metric": "value + unit + period, or null",
  "source_title": "...",
  "source_url": "direct link",
  "source_date": "YYYY-MM-DD",
  "evidence_type": "filing|earnings|regulator|company|website|research|news|sentiment",
  "confidence": "high|medium|low",
  "interpretation": "why it matters for this engagement",
  "open_question": "what still needs validation, or null",
  "confidential": false
}
```

**Assignments:**

1. **Company and financials.** Cover the business model, revenue by segment, the latest annual and quarterly results, guidance, capex, the strategy stated in filings and on calls, leadership changes, and the last 90 days of material news. Identify the 6 to 10 KPIs this industry is judged on, report the company's latest value for each, and name the benchmark or peer median where one is available. Useful examples of KPIs by industry:
   - Utilities: rate base growth, allowed ROE, O&M per customer, SAIDI/SAIFI, load growth, customer satisfaction such as the J.D. Power score.
   - SaaS: ARR, net revenue retention (NRR), CAC payback, gross margin.
   - Banking and auto finance: net interest margin (NIM), charge-offs, penetration rate.
   - Retail: same-store sales, inventory turns.
   - Across industries: NPS where it is disclosed.
2. **Investor and market view** (public companies only). Cover price performance against the sector index over 1 year and year to date, valuation multiples against peers, the consensus rating mix and price-target range, recurring questions on the earnings call, short interest, and notable institutional or activist moves. Present bull and bear arguments separately. Treat quant and retail sentiment as sentiment only, and never present it as a consensus.
3. **Industry and funding.** Cover the industry's evolution over the last 10 to 15 years in brief, its current state, market size and growth (naming who made each estimate), the major innovations and products being built, and business model shifts. For the funding radar, report venture and private equity funding into this sector and its subsectors over the last 4 to 8 quarters, how the sector ranks against other sectors, notable rounds, and the most active investors.
4. **Customers and segments.** Map the customer buckets for this company and the industry. For each bucket, give the need, the approximate share of revenue or volume when disclosed, the growth trend, the buyer versus the user versus the influencer, and the switching costs. Also cover emerging segments. When the scope is an internal tool, include internal user groups.
5. **Competitors.** Classify each competitor, with evidence, as one of the following:
   - Incumbent: a direct peer with the same business model.
   - Adjacent: a company from a neighboring industry that can reach the same customer need.
   - Insurgent: a startup or new business model attacking the value chain.

   Aim for 3 to 5 competitors of each type. For each one, give what it is doing differently, recent launches or moves, evidence of traction, and the threat it poses to the client.
6. **SPEED-C and regulation.** Assess the Societal, Political, Economic, Environmental, Demographic, and Competitive drivers. For each, give 2 to 4 specific current forces, the direction of each force (tailwind or headwind), its time horizon, and the likely effect on the company. Include pending legislation and rulings from regulators.
7. **Signals.** Return one JSON object (not records) with `checked`, `hiring`, `posts`, `news` and `feeds`:
   - `hiring`: current open roles from the official careers page only, including the job board it links to. No third-party job sites. Group roles by `team`, `location` and `seniority` in `groups`, count the skills and tools named in `skills`, list up to 10 `notable_roles`, and give `total_open`. Set `status` to `ok`, `not_found` or `unreadable`; never guess numbers.
   - `posts`: public LinkedIn posts by the company's employees and leaders that appear in search results, from the last 90 days. Keep only business signals: hiring pushes, launches, team announcements. Each has `author`, `author_title`, `date`, `summary` and `url`. Do not build profiles of individuals.
   - `news`: from RSS feeds (the company newsroom feed, a Google News RSS feed for the company name, the industry's main trade publications) and industry press, from the last 30 days. Each has `title`, `outlet`, `date`, a one-line `tldr`, `url`, and `paywalled` (true means headline-only TL;DR).
   - `feeds`: the RSS feed URLs used.

   Return exactly this shape. The hub reads these keys, and `scripts/build_hub.py` rejects other shapes:

   ```json
   {
     "checked": "YYYY-MM-DD",
     "hiring": {"status": "ok", "careers_url": "https://...", "board_url": "https://... or null", "total_open": 42,
                "groups": [{"dimension": "team", "name": "Engineering", "count": 12}],
                "skills": [{"name": "Python", "count": 6}],
                "notable_roles": [{"title": "...", "team": "...", "location": "...", "url": "https://..."}]},
     "posts": [{"author": "...", "author_title": "...", "date": "YYYY-MM-DD", "summary": "...", "url": "https://..."}],
     "news": [{"title": "...", "outlet": "...", "date": "YYYY-MM-DD", "tldr": "...", "url": "https://...", "paywalled": false}],
     "feeds": ["https://..."]
   }
   ```

   `dimension` is `team`, `location` or `seniority`. When `status` is `not_found` or `unreadable`, leave the hiring lists empty.

## Step 6: Merge and verify

Merge the records from agents 1 to 6 and the client document records, and give each an `id`: `r001`, `r002` and so on. Then verify, yourself or with one more agent for a large run:

- Spot-check the 10 records that matter most by re-fetching their sources, starting with the numbers the podcast's cold open and the outputs' "so what" lines will use.
- Flag records that conflict and show both values. Do not average them.
- Downgrade the confidence of stale or single-source claims.
- Make sure every `website` claim has an independent source, or is labeled a company claim.
- Where the SOW and public evidence disagree, show both side by side and turn the gap into a question for the client.
- List coverage gaps as open questions for the client.

## Step 7: Build the outputs

Follow, in order:

1. The role file's four outputs, written into `hub.json` as `outputs/hub.md` describes. If an agent behind an output failed, mark that output incomplete.
2. The podcast, as `outputs/podcast.md` describes, using the role file's podcast segment.
3. The Miro board, if the user wanted one, as `outputs/miro.md` describes.
4. The hub build, as `outputs/hub.md` describes.

## Step 8: Save and finish

Everything goes in `clients/<company-slug>/` in the working directory:

- `hub.html` and `hub.json`
- the podcast audio and `podcast-script.md`
- `evidence.json`: the verified records
- `signals.json`: the Signals agent's object

Open the hub for the user. End with two or three sentences: where the hub is, whether the podcast has audio, and the 2 or 3 most important data gaps to raise with the client. If an SOW was used, remind them the hub and podcast contain confidential client material.

## Step 9: Offer the daily newsletter

Follow `outputs/newsletter.md`.
