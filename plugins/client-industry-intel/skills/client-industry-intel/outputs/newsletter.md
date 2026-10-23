# Daily newsletter

Offered at the end of every run. It replaces the weekly monitoring of earlier versions.

## 1. Offer it

Ask: "Want a daily newsletter on <Company>? It covers only what's new in the last 24 hours." If no, stop.

## 2. Choose delivery

Check which connector tools are available, then offer only the routes that work:

| Route | When to offer |
|---|---|
| Gmail | A Gmail tool that sends messages is available |
| Slack | A Slack tool that posts messages is available |
| Email address only | Only if an email-sending service and its key are set up; otherwise explain that Claude can't send to an address without Gmail, Slack or a sending service, and offer to wait while the user connects Gmail or Slack |

Then ask for the destination (email address, or Slack channel or "message me") and a delivery time, defaulting to 8:00 in the user's timezone.

Store the address or channel only in the scheduled task. Never write it to a file.

## 3. Create the scheduled task

Create a daily routine: a scheduled cloud task that runs on Anthropic's cloud, not the user's machine. Use the `RemoteTrigger` tool's `create` action, or the `/schedule` command if that tool isn't available. Include the delivery connector (Gmail or Slack) in the routine. Never use `CronCreate` or a local cron job: those stop when the session or computer does. Give it the daily task prompt below with every `<...>` filled in from this run. If creating it fails, tell the user why and do not retry silently.

## 4. Confirm

Tell the user the delivery route, the time, and that the first newsletter arrives tomorrow.

## Daily task prompt

```
Write and send today's newsletter on <Company> for a <role label>.

Look only at the last 24 hours:
1. Official careers page: <careers URL> (and <job board URL> if it is the board the official page links to). List roles posted in the last 24 hours, with team and location. Use no other job sites.
2. LinkedIn: public posts by <Company>'s employees and leaders that appear in web search. Keep only business signals: hiring pushes, launches, team announcements. Name the person and title as the source. Do not build profiles of individuals.
3. News: these feeds and outlets: <RSS feed URLs and trade publications from this run>, plus a news search for "<Company>". One-line TL;DR per item with its link. Mark paywalled items as headline only.

Then add one or two lines on what today's items mean for a <role label> working on: <the user's task in their words, with no client document content>.

Format: subject "<Company> daily: <the most important item in a few words>". Sections: Top item, News, People's posts, New roles, What it means for you. If nothing is new, send one line: "Nothing new on <Company> in the last 24 hours."

Deliver via <Gmail to <address> | Slack to <channel>>.
```

## Rules

- The newsletter must never include content from the client's proposal or SOW. It leaves the user's machine.
- Hiring items come only from the official careers page and the job board it links to.
- Only items dated within the last 24 hours. No padding.
- Every item has a source link.
