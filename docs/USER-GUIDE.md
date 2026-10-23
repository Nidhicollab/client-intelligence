# User guide: how to run the client hub, step by step

This guide walks you through one full run of `client-industry-intel`, from install to your daily newsletter. It shows what to type, what the skill asks back, and how to answer. A run takes about 20 to 40 minutes, most of it research you don't have to watch.

## Before you start

| You need | Why | How to get it |
|---|---|---|
| Claude Code | Runs the skill | [Install Claude Code](https://docs.claude.com/en/docs/claude-code) |
| Web search turned on | All research is live | On by default in Claude Code |
| Gmail or Slack connected | Only for the daily newsletter | [claude.ai/customize/connectors](https://claude.ai/customize/connectors) |
| Miro connected | Only if you want a Miro board | Same page |
| A Mac, or an `OPENAI_API_KEY` or `ELEVENLABS_API_KEY` | Only for podcast audio | Without one, you get the podcast script |

## Step 1: Install the plugin (once)

In Claude Code, type:

```
/plugin marketplace add Nidhicollab/client-intelligence
/plugin install client-industry-intel@client-intelligence
```

Check it worked: `/plugin` should list `client-industry-intel` at version 2.0.0.

To get updates later: `/plugin marketplace update client-intelligence`.

## Step 2: Pick a working folder

Everything the skill makes is saved in `clients/<company>/` inside the folder where you start Claude Code. Use one folder for all your client work, for example:

```
mkdir -p ~/client-hubs && cd ~/client-hubs && claude
```

Don't run it inside this repo, so client files never end up in git.

## Step 3: Start the run

Give it the company's website URL. Any of these work:

> Build a client hub for https://www.duke-energy.com

> I'm starting a new engagement with https://stripe.com. Build me a client hub.

> Use client-industry-intel on https://www.toyotafinancial.com

**Tips**
- Use the company's main website, not a news article or LinkedIn page.
- For a subsidiary, give the subsidiary's own site. The skill finds the parent that files the reports.
- If you already know your role and task, put them in the first message. The skill will skip asking again:

> Build a client hub for https://stripe.com. I'm the engineering lead. We've been asked to design a payments-reconciliation service that plugs into Stripe's APIs. Focus: platform and API roadmap.

## Step 4: Confirm the company

The skill reads the site, then shows a short summary: company name, legal entity, public or private, parent company, industry, segments and careers page. Each item is marked **confirmed** (with a source) or **unconfirmed**.

**What to do:** read it and reply.

> Looks right, go ahead.

> Correct one thing: the engagement is with Toyota Motor Credit Corporation, not the parent.

Research doesn't start until you reply, so this is your chance to catch the wrong entity.

## Step 5: Tell it about you

The skill asks four things in one message. Answer them in one reply:

| It asks | Example answer |
|---|---|
| **1. Your role, by number** | `2` (engineering lead) |
| **2. What you've been asked to build or change** (2 or 3 lines) | "Modernize outage dispatch for field crews. Mobile tool, integrated with the outage management system." |
| **3. Project or idea focus** | "Crew response time" |
| **4. Proposal and SOW (optional)** | Drag the files into the prompt, or type their paths |

The five roles:

| # | Role | Your four visuals (after the podcast) |
|---|---|---|
| 1 | Product manager | Opportunity tree, stakeholder map, competitor landscape, experiment cards |
| 2 | Engineering lead or architect | Tech landscape, data flow diagram, technical risk heatmap, build-vs-buy grid |
| 3 | UX or product designer | Persona cards, journey map, service blueprint, competitor experience teardown |
| 4 | Engagement lead or partner | Stakeholder power map, SOW scope vs priorities, SPEED-C timeline, meeting prep card |
| 5 | Business or data analyst | KPI dashboard, metric tree, data source map, financial trend charts |

If your role isn't listed, describe it. The skill picks the closest one and tells you which.

**About the SOW:** it is read on your computer only. Nothing from it goes into a web search, and nothing from it is ever put in the newsletter. The hub gets a "Contains confidential client material" badge.

Then you'll get up to two quick choices:

- **Podcast voice:** "Mac voice" (one narrator), or "Text-to-speech service" (two hosts, only offered if you have an API key set).
- **Miro board:** yes or no (only offered if Miro is connected).

## Step 6: Wait for the research

Seven research agents run at the same time. Then the skill re-checks the most important sources and flags conflicts. You don't need to do anything. If Claude Code asks permission for web fetches, approve them.

## Step 7: Open your hub

When it finishes, the skill opens `clients/<company>/hub.html` and tells you:
- where the hub is,
- whether the podcast has audio,
- the 2 or 3 biggest data gaps to raise with the client.

The hub has a tab for the podcast, one tab per visual, a **Signals** tab (hiring, LinkedIn posts, news) and a **Sources** tab. Every claim links to its source. Anything the skill couldn't find says "not publicly available" rather than a guess.

Want a second role's view of the same company? Run again with the other role. Each run makes its own hub.

## Step 8: Set up the daily newsletter

At the end, the skill asks:

> Want a daily newsletter on Stripe? It covers only what's new in the last 24 hours.

Say yes, then answer:

| It asks | Example answer |
|---|---|
| **Delivery** | Gmail, or Slack (only routes you've connected are offered) |
| **Where to send it** | Your email address, a Slack channel, or "message me" |
| **What time** | Default is 8:00 in your timezone |

Each newsletter is a scheduled task in Anthropic's cloud, so it keeps running when your computer is off. The first one arrives the next morning.

Each email has: Top item, News, People's posts, New roles, and What it means for you. On quiet days you get one line: "Nothing new on <Company> in the last 24 hours."

## Newsletters for several companies

Each run sets up one newsletter for that run's company. For another company, run the skill on its URL and say yes at the end. You can have as many as you like, each with its own time and destination.

**See, pause or delete your newsletters:** go to [claude.ai/code/routines](https://claude.ai/code/routines). Each one is listed as "<Company> daily newsletter". You can also ask Claude Code:

> List my scheduled routines

> Pause the Stripe daily newsletter

> Change the Duke Energy newsletter to 7:00

Times are stored in UTC, so a newsletter set for 8:00 shifts by an hour when daylight saving starts or ends. Ask Claude to move it back if that matters to you.

## Good prompts and bad prompts

| Instead of | Try | Why |
|---|---|---|
| "Research Stripe" | "Build a client hub for https://stripe.com" | The URL tells it exactly which company |
| "I'm a consultant" | "I'm the engagement lead (4)" | Your role picks your four visuals |
| "Help with their tech" | "Design a reconciliation service on Stripe's APIs" | Your task shapes the research and the "so what" lines |
| Pasting SOW text into the chat | Dragging in the SOW file | The file stays local and gets the confidential handling |

## Troubleshooting

| Problem | What to do |
|---|---|
| "The site blocks automated reading" | Give the company name. The skill continues from public sources. |
| Wrong company or entity in step 4 | Correct it in your reply. Research hasn't started yet. |
| No podcast audio | You're not on a Mac and have no API key. You still get `podcast-script.md`. |
| Hub diagrams don't draw | The hub loads its chart library from the internet. Open it while online. |
| Newsletter didn't arrive | Check your spam folder, then [claude.ai/code/routines](https://claude.ai/code/routines) to see whether it ran and why it failed. |
| Newsletter not offered by email | Connect Gmail or Slack at [claude.ai/customize/connectors](https://claude.ai/customize/connectors) and run again. |
| Signals tab says "not found" for hiring | The skill couldn't find an official careers page. It never uses third-party job sites. |

## What you'll find on disk

```
clients/<company>/
  hub.html             open this
  hub.json             the hub's data
  podcast-script.md    the podcast script
  podcast.m4a or .mp3  audio, if made
  evidence.json        every verified finding with its source
  signals.json         hiring, posts and news
```
