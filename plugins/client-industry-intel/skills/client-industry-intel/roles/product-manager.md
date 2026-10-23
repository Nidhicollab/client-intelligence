# Role: Product manager

The reader frames problems, sets the roadmap and decides what to test first. Lead with opportunities and the riskiest assumptions, not company history.

## Research asks

Add these to the named agents' assignments:

- **Customers and segments:** customer complaints and unmet needs per segment, from reviews, support communities and forums (label these as sentiment), and from analyst or press coverage.
- **Company and financials:** every product launch, retirement and major update in the last 12 months, with dates.
- **Signals:** product management and product design roles on the careers page, and what products they name.

## Outputs

### 2. Opportunity tree

**Visual:** `mermaid` (`flowchart TD`)

- Root node: the outcome the SOW is buying. Without an SOW, use the outcome in the user's task description and say so in the caption.
- Second level: 3 to 5 problems or opportunities that block or serve that outcome.
- Third level: 1 to 3 hypotheses under each, labeled `H1`, `H2` and so on. Use the same labels in output 5.
- Add `(SOW)` to any node that comes from the client documents.
- Evidence: at least one record behind every second-level node.

### 3. Customer and stakeholder map

**Visual:** `mermaid` (`flowchart LR`)

- One `subgraph` per customer segment, with three nodes inside: buyer, user and influencer, each with a job title.
- An edge from each segment to a node naming its main need.
- Mark revenue share on the subgraph title when it is disclosed, for example `Residential (62% of revenue)`.
- Evidence: the customers agent's records for each segment.

### 4. Competitor landscape

**Visual:** `table`

- Columns: `Type`, `Competitor`, `What they do differently`, `Recent move`, `Threat to client`.
- `Type` is Incumbent, Adjacent or Insurgent. 3 to 5 rows of each where evidence allows.
- `Threat to client` cells use `level` high, medium or low.
- Evidence: the competitors agent's records.

### 5. Hypothesis and experiment cards

**Visual:** `cards`

- One card per hypothesis from output 2, titled `H1: <hypothesis>`.
- Body lines, in order: `Why we think so: ...`, `Cheapest test: ...`, `Signal it's true: ...`, `Ask in interviews: ...`.
- Tags: the confidence of the evidence behind it.
- A final card titled `What would change our view`, with 3 lines.
- Across the cards, include 5 to 8 stakeholder interview questions in total.

## Podcast segment

About 400 words for the product manager: the two or three biggest opportunities, the riskiest assumption behind them, and the first test worth running.
