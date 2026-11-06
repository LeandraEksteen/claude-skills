# Fork prompt template

A side session starts with no context. The prompt must stand alone. Pass inputs by path, never by pasting
their content. Save the filled prompt to `forks/<name>-prompt.md` and show it to the user. Never send it
anywhere yourself.

```markdown
You are a side session of an ongoing investigation. You start cold; everything you need is below.

## Goal
[One or two sentences: the question this fork answers, and why it matters to the investigation.]

## Read first (by path)
- [<root>/<slug>/INDEX.md]: goal, constraints, decisions, parked items. Read this first.
- [<root>/<slug>/topics/<area>.md]: only this topic file. Do not read log.md in full; grep it if needed.
- [other inputs: repo path and commit, data source, doc link]

## Do
- [specific tasks, in order]

## Constraints
- Read-only: do not edit, commit, push, post or send anything. Write only the output file below.
- Decisions already made and parked items in INDEX.md stand; do not reopen them.
- No personal data in notes or output.
- [model hint if cheap: "use a cheaper model for fan-out reading"]

## Output (by path)
Write everything to: [<root>/<slug>/forks/<name>-output.md]
Structure: Findings, Proposals, Gaps, Sources read.

## Labelling
- Every claim: `[verified: <pointer>, <date>]` only if you read it yourself from the primary source.
- `[inferred: <basis>]` for anything reasoned, or relayed from a source you did not open.
- `[proposal]` for recommendations and design choices; keep them under Proposals.
- Never present vendor, marketing or secondhand claims as verified.

## Finish
When the output file is written, reply with its path and a three-line summary, then stop.
```

## After the fork

Set its row in the INDEX Forks table to `running` when the user starts it and `done` when the output file
exists. Read the output file, keep its labels, spot-check the claims that matter before promoting any
`inferred` to `verified`, fold the findings into the topic files, and fill the "Folded into" column.
