# Role: Business or data analyst

The reader works with the numbers. Lead with KPIs and their sources, keep reported figures separate from estimates, and show the gaps.

## Research asks

- **Company and financials:** 3 to 5 years of history for each industry KPI; segment-level revenue and margin where reported.
- **Industry and funding:** peer benchmarks and medians for each KPI, naming who published them.
- **Signals:** data, analytics and BI roles on the careers page, and the tools they name.

## Outputs

### 2. KPI dashboard against benchmarks

**Visual:** `table`

- Columns: `KPI`, `Client value`, `Period`, `Benchmark or peer median`, `Gap`, `Source`.
- 6 to 10 KPIs from the industry KPI library.
- `Gap` cells use `level`: high when the client is clearly worse than the benchmark, medium when close, low when better.
- Write `not publicly available` where a value is missing, and name the proxy.

### 3. Metric tree

**Visual:** `mermaid` (`flowchart TD`)

- Root: the business outcome the SOW or task targets.
- Second level: 3 to 5 driver metrics. Third level: the input metrics behind each.
- Put the latest value and period in the node label when known, for example `O&M per customer: $310 (FY2025)`.

### 4. Data source map

**Visual:** `table`

- Columns: `Metric`, `Where it comes from`, `Frequency`, `Latest period`, `Gap or proxy`.
- One row per metric in outputs 2 and 3.
- `Where it comes from` names the evidence type: filing, regulator, company, research, estimate or client document.

### 5. Financial trend charts

**Visual:** `chart`

- A Chart.js line chart of revenue by segment over 3 to 5 years, using reported figures only.
- If segments are not reported, chart total revenue and operating margin instead, and say why in the caption.
- Label the unit and currency on the y axis.

## Podcast segment

About 400 words for the analyst: where the client beats and trails its peers, which numbers are solid and which are estimates, and the data to request first.
