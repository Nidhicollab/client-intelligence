# Role: Engineering lead or architect

The reader has to judge what can be built, on what, and what will break. Lead with the systems and integrations, and be explicit about what is inferred.

## Research asks

- **Signals:** every engineering, data and IT role on the careers page; count the languages, platforms, clouds and vendors they name.
- **Company and financials:** vendor case studies and press releases naming the client; partnership announcements; cloud and platform choices; major system migrations; public outages or security incidents in the last 24 months.
- **Competitors:** technology-led differences (platforms, APIs, data products) for each competitor.

## Outputs

### 2. Current tech landscape

**Visual:** `mermaid` (`flowchart LR`)

- One `subgraph` per layer: `Customer channels`, `Core systems`, `Data and analytics`, `Infrastructure and cloud`.
- One node per system or vendor, labeled `<System> (<vendor>)`.
- Add `(inferred)` to any node supported only by job postings, and `(SOW)` to nodes from the client documents.
- Evidence: every node traces to a record.

### 3. Data flow and integration diagram

**Visual:** `mermaid` (`flowchart LR`)

- The thing the SOW asks to build, in the middle.
- Left: the source systems and data it needs. Right: the people and systems that consume it.
- Label edges with the data that moves. Use `?` in the label where the interface is unknown.
- Without an SOW, draw it from the user's task description and say so in the caption.

### 4. Technical risk and dependency heatmap

**Visual:** `table`

- Columns: `Risk or dependency`, `Area`, `Likelihood`, `Impact`, `Evidence`, `Next question`.
- `Likelihood` and `Impact` cells use `level` high, medium or low.
- 6 to 10 rows. Include at least one row for each known legacy system and each third-party dependency.

### 5. Build-vs-buy vendor grid

**Visual:** `table`

- Columns: `Capability`, `Build notes`, `Vendor options`, `Client already uses`, `Lean`.
- 4 to 8 capabilities the SOW or task needs. 2 or 3 vendors per capability.
- `Lean` is Build, Buy or Unclear, and is labeled as interpretation in the caption.

## Podcast segment

About 400 words for the engineering lead: what the stack most likely looks like, the hardest integration, and what to confirm in the first technical session.
