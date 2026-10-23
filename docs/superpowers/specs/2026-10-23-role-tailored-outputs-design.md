# client-industry-intel v2: URL intake, role-tailored outputs, daily newsletter

Date: 2026-10-23
Status: draft for review
Replaces: the v1 flow in `plugins/client-industry-intel/skills/client-industry-intel/SKILL.md` (intake questions, single Claude Doc briefing, weekly monitoring)

## Goal

A consulting team member gives the company's website URL, their role, and their project context. The skill researches and fact-checks the company and returns five outputs built for that role: a 15-minute podcast and four visuals. These replace a long document. A daily newsletter then reports what changed.

Success means:

- Starting needs only a URL. Every other company fact is found and confirmed by the skill.
- Each of the five roles gets outputs it would actually use, and every claim traces to a source.
- Client documents shape the outputs but never leave the machine through web searches.
- Peers install it with the same two plugin commands, with no account needed beyond what each feature names.

## Non-goals

- Roles beyond the five listed. Any other role maps to the closest one.
- A long-form briefing document. The v1 Claude Doc is dropped.
- Updating the hub after it is built. Users re-run the skill for a fresh hub.
- Following social accounts, or reading anything that needs a login.
- Scraping LinkedIn.

## File structure

```
plugins/client-industry-intel/
  .claude-plugin/plugin.json          version 2.0.0
  skills/client-industry-intel/
    SKILL.md                          the flow; points to the files below
    roles/
      product-manager.md
      engineering-lead.md
      ux-designer.md
      engagement-lead.md
      data-analyst.md
    outputs/
      podcast.md                      script format and audio steps
      hub.md                          how to fill the hub template
      miro.md                         how to build the optional Miro board
      newsletter.md                   daily newsletter setup and format
    templates/
      hub.html                        fixed layout for every hub
    scripts/
      make_podcast.py                 Mac voice or text-to-speech service
      build_hub.py                    validates hub.json and renders the hub
```

`SKILL.md` stays short and holds the flow. Claude opens a role or output file only when that step runs, so it reads one role file per run, not five.

Each `roles/<role>.md` file contains the extra research asks for that role, its four outputs (what each shows, the diagram or chart type, the evidence it needs), and the role-specific podcast segment.

## Flow

URL → confirm the company → about you → read client documents → research (seven agents) → verify → build outputs → save → offer the daily newsletter.

### 1. URL

The user pastes the company's website URL, either in their first message or in answer to the first question. Claude reads the site's key pages (about, products, investor relations, newsroom, leadership, careers) and works out:

- company name and legal entity
- public, private or subsidiary, and for a subsidiary the parent that files reports
- industry, geography, segments and main products
- the official careers page URL, and the job board behind it if it sends applicants to one

If the site blocks automated reading, Claude asks for the company name and continues from that.

### 2. Confirm the company

Claude shows a short "here's what I found" summary. Each item is checked against an independent source (filing, regulator or major press) and marked confirmed or unconfirmed. Where parent and subsidiary are unclear, Claude asks. The user corrects anything before research starts.

### 3. About you

Two prompts.

Multiple choice (one AskUserQuestion call):

- Role: product manager, engineering lead or architect, UX or product designer, engagement lead or partner, business or data analyst.
- Podcast voice: Mac voice, or a text-to-speech service. The service option appears only if `OPENAI_API_KEY` or `ELEVENLABS_API_KEY` is set. On a machine that is not a Mac and has no key, the podcast is script only, and the skill says so.
- Miro board: yes or no. Offered only if the Miro connector is available.

Free text (one plain message):

- 2-3 lines on what they have been asked to build or change
- the project or idea focus
- optional file paths, or drag-and-drop, for the client's proposal and SOW

Every run is full depth. The investor view runs automatically for public companies. The funding radar always runs.

### 4. Read client documents

If the proposal or SOW is given, Claude reads them locally and extracts scope and deliverables, timeline, named stakeholders and success criteria. If a file is a scanned PDF Claude cannot read, it asks for a text version or continues without it.

Confidentiality rules:

- Client document content is never placed in a web search query.
- Agents receive a short scope summary written by Claude, with no names of client staff, no figures, and no contract terms.
- Every record from a client document is flagged confidential.

### 5. Research: seven agents in parallel

The six v1 agents stay, with their v1 assignments: company and financials, investor and market (public companies only), industry and funding, customers and segments, competitors, SPEED-C and regulation.

Each agent also receives the confirmed company profile, the role, task and focus, the scope summary, and the extra research asks from the role file:

| Role | Extra research asks |
|---|---|
| Product manager | Customer complaints and unmet needs, recent product launches |
| Engineering lead | Tech stack clues from job postings, vendor case studies, partnership announcements, cloud and platform choices |
| UX designer | App store and review-site ratings, support complaints, competitors' digital experiences |
| Engagement lead | Leadership bios and tenure, recent org changes, board and activist pressure, consulting firms named in press |
| Data analyst | KPI history over 3 to 5 years, segment-level figures, peer benchmarks |

A seventh agent, **Signals**, covers three sources:

- **Hiring:** current open roles from the official careers page only, including the Greenhouse, Lever, Workday or other board the official page links to. No third-party job sites. Roles are grouped by team, location, seniority and skills named, with the date checked.
- **LinkedIn:** public posts by the company's employees and leaders that appear in search results. This is a sample, not a full feed. Only business signals are kept (hiring pushes, launches, team announcements), with name and title as the source. No profiles of individuals.
- **News TL;DRs:** RSS feeds (company newsroom, a Google News feed for the company name, the industry's main trade publications) and industry press. One line per item with a link. Paywalled items get a headline-only TL;DR, marked as such.

### 6. Evidence records

The v1 record schema stays, with two changes:

- `evidence_type` adds `website` and `client_document`.
- A new boolean field, `confidential`, is true for every `client_document` record.
- A new string field, `id` (`r001`, `r002`, ...), assigned when the records are merged, so outputs can point to the records behind them.

### 7. Verify

v1 verification stays: spot-check the 10 most important records by re-fetching sources, show conflicting values side by side, downgrade stale or single-source claims, turn gaps into client questions. Two additions:

- Every claim sourced only to the company's website needs an independent source, or it is labeled a company claim.
- Where the SOW and the public evidence disagree, both appear side by side and the gap becomes a client question.

### 8. Outputs

Everyone gets the podcast as output 1. Outputs 2 to 5 depend on the role:

| Role | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| Product manager | Opportunity tree: SOW goals down to problems and hypotheses | Customer and stakeholder map (buyer, user, influencer) | Competitor landscape (incumbent, adjacent, insurgent) | Hypothesis and experiment cards, with interview questions |
| Engineering lead or architect | Current tech landscape, marked where inferred | Data flow and integration diagram for what the SOW asks to build | Technical risk and dependency heatmap | Build-vs-buy vendor grid |
| UX or product designer | Persona cards, one per segment | Customer journey map with pain points | Service blueprint: touchpoints and supporting systems | Competitor experience teardown |
| Engagement lead or partner | Stakeholder power and interest map | SOW scope against stated client priorities: alignment, gaps, follow-on work | SPEED-C tailwinds and headwinds on a timeline | Meeting prep card: talking points, questions, what would change our view |
| Business or data analyst | KPI dashboard against benchmarks | Metric tree from business outcome to drivers | Data source map: where each number comes from, and the gaps | Financial trend charts by segment |

Without an SOW, outputs that depend on it (opportunity tree, data flow diagram, SOW scope map) use the task description and focus instead, and say so.

**Podcast** (`outputs/podcast.md`, `scripts/make_podcast.py`):

- About 2,200 words, roughly 15 minutes spoken.
- Running order: cold open; the company in two minutes; industry and competitors; a segment for the listener's role; risks and signals; what to do this week.
- Mac voice: one narrator, using the built-in `say` command, converted to `.m4a` with the built-in `afconvert`.
- Text-to-speech service: two hosts in conversation, using OpenAI or ElevenLabs, whichever key is set. The script is sent in chunks within the service's per-request limit and the audio files are joined.
- The script is always saved, so the user has it even if audio fails.
- Confidential details from the SOW may appear in the script, so the podcast is marked confidential when an SOW was used.

**Hub** (`templates/hub.html`, `outputs/hub.md`):

- Top bar: company name, as-of date, role, and a "Contains confidential client material" badge when an SOW was used.
- Seven tabs: Podcast (audio player and script), the four role outputs, Signals, Sources.
- Each output opens with a two-line "so what", then the diagram or chart, then its evidence with source links. Estimates and inferences are labeled.
- Diagrams use Mermaid and charts use Chart.js, each loaded from a version-pinned CDN link. The hub needs an internet connection to draw them.

**Miro** (optional, `outputs/miro.md`): one board with a frame per diagram output (trees, maps, journeys, blueprints, data flow). The hub links to the board. If Miro is not connected, it is skipped and the hub notes it.

### 9. Save

All files go in `clients/<company-slug>/` in the working directory:

- `hub.html`
- `podcast.m4a` (or the service's format) and `podcast-script.md`
- `evidence.json`
- `signals.json`

### 10. Daily newsletter

Offered at the end of the run. It replaces v1's weekly monitoring.

- **Schedule:** a daily scheduled cloud task, created with the same scheduling route v1 used. It does not depend on the user's computer or the local hub files.
- **Content:** only items from the last 24 hours: news TL;DRs, LinkedIn posts by company people, new roles on the official careers page, and one or two lines on what they mean for the user's role. If nothing is new, a one-line email saying so.
- **No client document content** goes into the newsletter, because it is sent outside the local machine.
- **Delivery,** chosen at setup:

| User's setup | Delivery |
|---|---|
| Gmail connected to Claude | Email from their Gmail to the address they give |
| Slack connected | Slack message to themselves or a channel |
| Neither | Requires an email-sending service and its API key; without one, the skill says it cannot send and offers Gmail or Slack setup |

- **Email address:** asked at setup and stored only in that user's scheduled task. No address is written into any file in the repo.

## Failure handling

| Problem | What happens |
|---|---|
| Website blocks automated reading | Ask for the company name; research from that |
| Parent and subsidiary unclear | Ask during confirmation, before research |
| No careers page, or it can't be read | Signals says so; no guessed hiring numbers |
| Not a Mac and no API key | Script only |
| Text-to-speech call fails | Fall back to Mac voice if available, else script only |
| Miro not connected | Skip; note it in the hub |
| SOW unreadable | Ask for a text version, or continue without it |
| An agent fails | Its section is marked incomplete; never filled with guesses |
| Newsletter delivery not possible | Say why at setup; do not create the scheduled task |

## Open items to verify during implementation

Implementation notes: the scripts are Python (standard library only) rather than shell, because chunking text for the speech services and validating the hub data are unreliable in shell. Peers already have `python3` because the plugin install requires git.

1. Whether the Gmail connector can send email or only create drafts. If drafts only, Slack becomes the recommended route.
2. Whether scheduled cloud tasks can use the user's Gmail and Slack connectors.
3. Which scheduling tool to call from the skill, given v1's `create_trigger` instruction.
4. Whether `say` and `afconvert` produce a 15-minute file in reasonable time.
5. The text-to-speech services' current per-request text limits and model names.

Resolved 1: not settled in this session, because no Gmail connector is connected here. The newsletter guide offers Gmail only when a Gmail tool that sends messages is available at setup time, so a drafts-only connector is never offered. Checked again in end-to-end testing.
Resolved 2: scheduled cloud routines run as full Claude Code cloud sessions and can include MCP connectors such as Slack (from third-party guides to the research-preview routines feature; Anthropic's own page was not found).
Resolved 3: create the routine with the `RemoteTrigger` tool's `create` action, or the `/schedule` command. `CronCreate` is session-only and expires after 7 days, so it is not used.
Resolved 4: `say` rendered 2,400 words in about 7 seconds and `afconvert` converted it in under 1 second. The Mac voice speaks about 180 words a minute and ignores slower `-r` rates, so a Mac-voice script targets about 2,700 words for 15 minutes; service scripts stay at about 2,200.
Resolved 5: OpenAI model `gpt-4o-mini-tts` with voices including alloy and nova (OpenAI's API reference page blocked automated reading; the 4096-character input limit is the long-standing documented value and is kept). ElevenLabs model `eleven_multilingual_v2`, header `xi-api-key`, 10,000-character limit per request; the script uses 5,000-character chunks.

Each item is resolved before the step that depends on it is built. If an item cannot be resolved, that part of the design changes and is brought back for review.

## Testing

- Three companies: one public, one private, one subsidiary.
- All five roles covered across those runs.
- A dummy SOW written for testing. No real client material.
- Each hub is checked for:
  - all diagrams and charts draw
  - podcast length between 13 and 17 minutes
  - source links resolve
  - the confidential badge appears when an SOW was used
  - no SOW content in any web search query or newsletter
- One newsletter is set up to the maintainer's own address and checked on two consecutive days.

## Release

- `plugin.json` version 2.0.0, with an updated description.
- `marketplace.json` plugin description updated.
- README updated: new intake, roles and outputs table, newsletter setup, requirements (Mac or API key for audio, Gmail or Slack for the newsletter, optional Miro).
- Peers get the new version by updating the marketplace.
