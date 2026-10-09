---
name: "client-industry-intel"
description: "Build a sourced client and industry intelligence briefing for a consulting PM entering a new client or industry; runs parallel research agents and can set up ongoing monitoring."
---

# Client & Industry Intelligence Briefing

Purpose: when a consulting PM starts with a new client or industry, produce one sourced briefing that covers the company, its industry, customers, competitors, KPIs, the investor view, SPEED-C drivers, and what it all means for the engagement. Every claim must trace to a source. Gaps are stated as gaps and never filled with plausible numbers.

The reference for tone and reasoning is a consulting transformation analysis. It moves from market pressures to incumbent, adjacent, and insurgent competitors, then to capability gaps and recommended actions. Quantify where sources allow, and say explicitly when exposure is inferred from industry trends instead of disclosed by the company.

## Step 1: Intake

Ask in one AskUserQuestion call for anything the request is missing. Skip questions it already answers:

1. **Company**, and whether it is public, private, or a subsidiary. For a subsidiary, name the parent that files the financial reports.
2. **Scope**: the whole enterprise, one business line, or one product or tool (for example an internal operations tool).
3. **Industry and geography**.
4. **Project focus**: what the engagement is about (digital transformation, a new product, operations, pricing, and so on).
5. **Depth**: a quick brief (about 15 minutes, fewer sources) or a full brief.
6. **Optional modules**: stock and market sentiment (public companies only) and a VC funding radar.

If no one is there to answer, choose the enterprise scope, full depth, and all modules, then state those assumptions at the top of the briefing.

## Step 2: Create the briefing doc first

Create a Claude Docs doc titled `<Company> — Client & Industry Brief`, using the docs skill if one is listed. Add an as-of date, a byline, and one pending placeholder for each section below. Open the doc so the PM can watch it fill in.

Sections:

1. Executive summary: the 5 most important findings and 3 implications for the engagement
2. Company snapshot: business model, segments, products, strategy, recent news
3. Financials and KPIs: the latest reported figures, plus the industry-standard KPIs and where the company stands on each
4. Investor and market view (optional module)
5. Industry landscape: how the industry evolved, where it stands now, innovations, and business model shifts
6. Funding and investment radar (optional module)
7. Customers and segments
8. Competitive landscape: incumbent, adjacent, and insurgent competitors
9. SPEED-C drivers
10. Implications for the PM: hypotheses, opportunities, risks, stakeholder interview questions, and questions to validate with the client
11. Sources and data gaps

## Step 3: Run the specialist researchers in parallel

The user asked for a multi-agent workflow, so spawn these researchers with the Agent tool in a single message so they run in parallel. Use subagent_type general-purpose. Pass each one the full intake context, its assignment below, the shared rules, and the output schema.

**Shared rules for every researcher:**

- Search the web. Prefer sources from the last 12 months, and mark anything older.
- Source priority, from highest to lowest: regulatory filings and regulators (10-K, 10-Q, 8-K, FERC, state PUCs, EIA, SEC), earnings materials and call transcripts, company releases, reputable research and industry bodies, major business press, and trade press. Blogs and forums count only as sentiment and must be labeled that way.
- Label every metric with its value, unit, reporting period, and reporting entity.
- Keep reported facts, analyst or third-party estimates, and your own interpretation separate.
- If data isn't public, return a record with the claim "not publicly available" and name the closest proxy.
- Return between 10 and 25 records.

**Output schema.** Each researcher returns a JSON array of records in this shape:

```json
{
  "section": "company|financials|investor|industry|funding|customers|competitors|speedc",
  "claim": "concise, checkable finding",
  "entity": "who it concerns",
  "metric": "value + unit + period, or null",
  "source_title": "...",
  "source_url": "direct link",
  "source_date": "YYYY-MM-DD",
  "evidence_type": "filing|earnings|regulator|company|research|news|sentiment",
  "confidence": "high|medium|low",
  "interpretation": "why it matters for this engagement",
  "open_question": "what still needs validation, or null"
}
```

**Assignments:**

1. **Company and financials.** Cover the business model, revenue by segment, the latest annual and quarterly results, guidance, capex, the strategy stated in filings and on calls, leadership changes, and the last 90 days of material news. Identify the 6 to 10 KPIs this industry is judged on, report the company's latest value for each, and name the benchmark or peer median where one is available. Useful examples of KPIs by industry:
   - Utilities: rate base growth, allowed ROE, O&M per customer, SAIDI/SAIFI, load growth, customer satisfaction such as the J.D. Power score.
   - SaaS: ARR, net revenue retention (NRR), CAC payback, gross margin.
   - Banking and auto finance: net interest margin (NIM), charge-offs, penetration rate.
   - Retail: same-store sales, inventory turns.
   - Across industries: NPS where it is disclosed.
2. **Investor and market view** (optional module, public companies only). Cover price performance against the sector index over 1 year and year to date, valuation multiples against peers, the consensus rating mix and price-target range, recurring questions on the earnings call, short interest, and notable institutional or activist moves. Present bull and bear arguments separately. Treat quant and retail sentiment as sentiment only, and never present it as a consensus.
3. **Industry and funding.** Cover the industry's evolution over the last 10 to 15 years in brief, its current state, market size and growth (naming who made each estimate), the major innovations and products being built, and business model shifts. For the funding radar, report venture and private equity funding into this sector and its subsectors over the last 4 to 8 quarters, how the sector ranks against other sectors, notable rounds, and the most active investors.
4. **Customers and segments.** Map the customer buckets for this company and the industry. For each bucket, give the need, the approximate share of revenue or volume when disclosed, the growth trend, the buyer versus the user versus the influencer, and the switching costs. Also cover emerging segments. For example, an energy company might serve residential, commercial, industrial, data centers and hyperscalers, EV charging, and wholesale or municipal customers. When the scope is an internal tool, include internal user groups.
5. **Competitors.** Classify each competitor, with evidence, as one of the following:
   - Incumbent: a direct peer with the same business model.
   - Adjacent: a company from a neighboring industry that can reach the same customer need.
   - Insurgent: a startup or new business model attacking the value chain.

   Aim for 3 to 5 competitors of each type. For each one, give what it is doing differently, recent launches or moves, evidence of traction, and the threat it poses to the client.
6. **SPEED-C and regulation.** Assess the Societal, Political, Economic, Environmental, Demographic, and Competitive drivers. For each, give 2 to 4 specific current forces, the direction of each force (tailwind or headwind), its time horizon, and the likely effect on the company. Include pending legislation and rulings from regulators.

## Step 4: Verify

After all the researchers return, merge the records and run a verification pass yourself, or use one more agent for a large brief:

- Spot-check the 10 records that matter most by re-fetching their sources, and prioritize numbers used in the executive summary.
- Flag records that conflict with each other and show both values. Do not average them.
- Downgrade the confidence of stale or single-source claims.
- List coverage gaps as open questions for the client.

## Step 5: Synthesize into the doc

Replace each placeholder section. Style rules:

- Lead each section with a two- or three-sentence "so what", then the evidence.
- Use tables for KPIs, competitors (with columns for type, what they do differently, recent moves, and threat level), customer segments, and SPEED-C drivers.
- Put live charts over the data where a chart helps, such as revenue by segment, the KPI trend, or the funding trend. Build them from the numbers, not as images.
- Cite inline with links. Mark estimates and inferences explicitly, for example: "Inferred from industry trend; company does not disclose."
- The PM implications section must include testable hypotheses, 5 to 8 stakeholder interview questions, and "what would change our view".

Describe the executive summary last, once everything else is written.

## Step 6: Save and offer monitoring

- Save a markdown copy of the brief and the raw evidence records to the attached Project, if there is one, at `clients/<company-slug>/brief.md` and `clients/<company-slug>/evidence.json`.
- Offer ongoing monitoring. If the PM accepts, create a weekly scheduled task (use create_trigger, never a local cron). Each run should do the following:
  1. Read the saved evidence and the last change log.
  2. Search for new earnings results, filings, regulatory actions, competitor launches, funding rounds, and leadership changes since the last run.
  3. Append a dated "What changed since last review" section to the doc. Each item gets a source and a one-line implication.
  4. Update the evidence file.

  Report only what is material. If nothing material changed, the run says so in one line.

## Finish

End with one or two sentences giving the doc link and the 2 or 3 most important data gaps the PM should raise with the client.