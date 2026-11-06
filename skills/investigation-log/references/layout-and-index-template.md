# Layout and INDEX.md template

```
<root>/<slug>/
  INDEX.md                  # the only file read on start/resume; keep to about 100 lines
  topics/<area>.md          # one per finding area (kebab-case)
  log.md                    # append-only, dated, searched with grep, never fully read
  forks/<name>-prompt.md    # the prompt given to a side session
  forks/<name>-output.md    # what the side session wrote back
```

## INDEX.md

Copy this, fill it in, delete nothing. Empty sections stay with "none yet".

```markdown
# [Investigation title]

## STATE (rewrite at milestones and before /compact; at most 10 lines)
- Updated: [YYYY-MM-DD HH:MM]
- Where we are: [one or two lines]
- Next step: [one line]
- In flight: [fork names, or none]
- Do not redo: [things already settled or checked]

## Goal
[One paragraph. The north star, in the user's words.]

## Constraints and stance
- [constraint, with who said it and when]

## Decisions made
- [YYYY-MM-DD] [decision]. Why: [reason]. Topic: [topics/area.md]

## Parked
- [item]. Why parked: [reason]. Revisit when: [condition]

## Open questions
- [question]. Owner: [who]. Topic: [topics/area.md]

## Shared doc
- Link: [url, or none]
- Section map: [doc section] -> [topics/area.md]
- Rules: edit only what is asked; ask before adding sections.

## Forks / side sessions
| Name | Prompt | Output | Status (drafted/running/done) | Folded into |
|---|---|---|---|---|

## Topics
| File | What it holds | Last updated |
|---|---|---|

## Pointers
- [source, repo, dashboard, person], each with one line on what it is for
```

## log.md

One line per entry, newest last: `YYYY-MM-DD HH:MM  [what was read or done]. [what changed]. [topic file]`.
Corrections are new lines, never edits. Notes about rejected or unreliable sources go here, not in topic
files or the shared doc.

## topics/<area>.md

Budget: about 150 lines. Past that, propose splitting the file (ask first) and update the INDEX Topics table.

```markdown
# [Area]
Scope: [one line]. Last updated: [date].

## Summary (at most 8 lines; read this with `head` before anything else in the file)
- [the conclusions a resuming session needs, each labelled]

## Findings
- [claim] [verified: path:line or query, 2026-10-09]
- [claim] [inferred: basis]

## Proposals
- [proposal] [proposal]

## Gaps
- [what is not checked yet]
```
