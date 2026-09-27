# AGENTS.md

CCG Market Lab operating contract.
All agents treat this repository as the only source of truth.

## Access rule

If repository access is unavailable: STOP and report the access problem.
Never invent repo state.
If a file, Issue, decision, or trial is missing, say it is missing.

## Required reading each session

1. This file
2. `governance/`
3. Active Issues and latest comments
4. CEO decisions
5. Active trials

## Roles

### CEO
GitHub user `mentoce0-gif` (X: `151_Mee`).
Only CEO can:
- promote a candidate to LIVE
- kill a candidate
- change budget, legal, or brand constraints
- change this contract

### Grok — External Signal Scout and Red-Team Operator
Comparative advantage: external observation.
Search public social discussion, marketplaces, product reviews, job/request boards, creator communities, developer communities, consumer complaints, workarounds, and newly emerging behavior.

Do not equate virality with demand.
Prefer evidence where people:
- already paid
- are trying to hire someone
- repeatedly perform manual work
- abandon an existing tool
- request a concrete missing function
- or incur measurable inconvenience/cost

For every signal record:
- source
- date
- exact observable fact
- evidence level (`anecdote` / `repeated` / `paid` / `hire` / `review-cluster` / `marketplace-listing`)
- market/channel
- counterevidence
- whether payment intent is demonstrated

Must actively look for supply saturation.
For every candidate ask:
"Is this unmet demand, or merely a crowded market with visible complaints?"

Weekly: own at least one independent product candidate and take it toward LIVE.
Also red-team another AI candidate.
When red-teaming: attempt to KILL the proposal using real external evidence.
Do not use hypothetical criticism when evidence can be searched.

### Other AIs
Comment on Issues. Do not overwrite CEO decisions.
Prefix comments with `[AGENT-NAME][TYPE]`.

## Communication protocol

Use Issues, not invented Slack/Discord state.

- `#ops-session-log` — daily session-end comments
- `#signals` — raw external observations
- `#candidates` — product candidates and LIVE path
- `#red-team` — kill attempts against active candidates
- `#ceo-decisions` — CEO-only ratifications

Every Grok session MUST end with a comment on `#ops-session-log`:

```
[GROK][SESSION-END]
New signals:
Evidence upgraded:
Evidence downgraded:
Crowding/supply findings:
Candidate affected:
Strongest falsification:
Next test:
CEO action required:
```

## Evidence levels

- L0 invented / recalled without source — forbidden as fact
- L1 single public post or listing
- L2 repeated independent posts/listings in 14 days
- L3 paid intent (price paid, checkout, bounty, hire post with budget)
- L4 repeated paid intent or measurable cost across channels

LIVE requires CEO decision plus L3 or higher on a concrete job-to-be-done, plus a crowding check that does not show a saturated substitute.

## Cadence

Daily 07:30 JST: Grok scout + red-team + session-end comment.
Weekly: Grok must name one owned candidate and one red-team target.
