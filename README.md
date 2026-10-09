# client-intelligence

A Claude plugin marketplace with one plugin, **client-industry-intel**. It turns the first week of research on a new client or industry into one command.

## Install

In Claude Code:

```
/plugin marketplace add Nidhicollab/client-intelligence
/plugin install client-industry-intel@client-intelligence
```

Then ask, for example: *"Run a client intel brief on Duke Energy, focused on operations and supply chain."*

## What it does

1. **Asks a few intake questions.** These cover the company, whether it is public, private or a subsidiary, the scope (enterprise, business line or product), the industry and geography, the engagement focus, and how deep to go.
2. **Runs six research agents in parallel:**
   - company and financials, plus the industry's KPIs
   - investor and market view
   - industry and VC funding
   - customers and segments
   - competitors, classed as incumbent, adjacent or insurgent
   - SPEED-C and regulation
3. **Returns findings in one evidence format.** Every finding includes a source URL, a date, the evidence type and a confidence level. Missing data is labeled "not publicly available" instead of being guessed.
4. **Verifies the findings.** It re-checks the sources behind the most important claims, shows conflicting figures side by side, and turns gaps into questions for the client.
5. **Writes the briefing.** Each section opens with its main takeaway, and the briefing ends with PM implications: testable hypotheses, interview questions, and what would change the view.
6. **Can keep the briefing current.** A weekly scheduled task adds a "What changed since last review" section.

## Layout

```
.claude-plugin/marketplace.json
plugins/client-industry-intel/
  .claude-plugin/plugin.json
  skills/client-industry-intel/SKILL.md
```

## Portability

`SKILL.md` is a plain-markdown format with YAML frontmatter, so other tools can use the same skill folder:

- Claude Code and Cowork load it through this marketplace.
- Agent tools that read `SKILL.md`, such as Codex CLI and Cursor, can use the same folder with their own marketplace or config file.

## License

MIT
