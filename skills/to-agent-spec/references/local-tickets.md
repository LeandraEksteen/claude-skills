# Local tickets

Used when there is no issue tracker. A "ticket" is then a markdown file in the work's workspace folder, and
every tracker action has a file equivalent. This file is copied into each skill that touches tickets
(`to-agent-spec`, `build`, `implement`, `test-plan`) so the skills stay self-contained when symlinked. Keep the
copies identical.

## When local mode applies

- The user says there is no tracker, or the work is local.
- The key starts with `LOCAL-` (for example `LOCAL-3`).
- No tracker connector is available and the user confirms working locally.

Never switch silently. If a tracker was expected and its connector fails, ask before falling back. Say once
which mode you are in: "Local mode: tickets are files under `<workspace-root>`." One work item uses one mode
from start to finish.

## Keys and folders

- Key: `LOCAL-<n>`. `n` is 1 plus the highest existing `local-<n>` folder name in `<workspace-root>`
  (`ls <workspace-root>`); start at 1 when none exist.
- Folder: `<workspace-root>/local-<n>/`, the lowercase key, so the lint's folder-name check passes.
- Work that starts from a conversation has a confirmed slug folder until its ticket is created. In local mode
  "create the ticket" means: write `ticket.md` in that folder, assign the next `LOCAL-<n>`, and rename the
  folder to `local-<n>`.

## ticket.md

```markdown
---
key: LOCAL-3
type: Task              # Task | Bug | Story | Epic
title: Remind users when a record stalls
status: To Do           # free text, for example To Do | In Progress | Done
parent: null            # LOCAL-<n> of the epic this belongs to, or null
updated: 2026-11-06T10:00:00Z   # set on every change, UTC
---

## Description
<context, scope, not in scope, edge cases, open questions, sources>

## Acceptance criteria
- <one checkable line each, `Req #` first when a spec exists>

## Comments
- 2026-11-06 <author or role>: <text>

## Children
- LOCAL-4: <title>
```

- Comments are append-only: one dated line per comment, never edited.
- `Children` exists on an epic only. Each child is its own `ticket.md` at
  `<workspace-root>/<key-lowercase>/ticket.md`, with `parent` set to the epic. A child may have children of its
  own (subtasks).
- No names, emails or amounts from real customers, same rule as everywhere.

## Tracker action to file action

| Tracker action | Local equivalent |
|---|---|
| Identity or health call | Check `<workspace-root>` exists and is writable. Nothing else. |
| Fetch a ticket | Read `ticket.md`: title, Description, Acceptance criteria, **every** comment. |
| Read an epic tree | Read the epic's `ticket.md`, then each key under `Children`, recursively, whatever its `status`. |
| Create a ticket | Draft it, show the full text, write the file only on a yes. Same structure as the tracker ticket. |
| Comment | Append one dated line under `## Comments`, then set `updated`. Show the text first and act only on a yes. |
| File a bug | Create a new `ticket.md` of type `Bug` with the next `LOCAL-<n>`; set `parent` only if asked. Only on a yes. |
| Change a field | Edit the frontmatter or section, then set `updated`. |
| Link to a ticket | Write the key, for example `LOCAL-3`. |

## Freshness

`requirements.yaml` keeps its tracker-named fields so the lint works unchanged:

- `key`: `LOCAL-<n>`.
- `jira_updated`: the ticket's `updated` value.
- `jira_content_sha`: sha256 of `title + "\n" + Description section text`, the same formula as for a tracker
  ticket. Comments do not change it, so a new comment never looks like an edit to the ask.

Compute it with:

```bash
python3 - <<'PY' "<workspace-root>/local-3/ticket.md"
import hashlib, re, sys
t = open(sys.argv[1], encoding="utf-8").read()
title = re.search(r"^title:\s*(.+)$", t, re.M).group(1).strip()
desc = re.search(r"^## Description\n(.*?)(?=^## |\Z)", t, re.M | re.S).group(1).strip()
print(hashlib.sha256((title + "\n" + desc).encode()).hexdigest())
PY
```

Set `jira_updated` after you append your own comment, so your comment does not look like someone else's
change. `state/<tracker>-snapshot.md` is not needed: the file is its own record.

## What changes in the other steps

- **Links.** A PR body or comment cannot link a file on one machine. Write `LOCAL-3 (local ticket)` and put
  the acceptance lines in the body, since a reviewer cannot open the ticket.
- **Sharing.** The workspace is outside any repo and is not shared. Tell the user once that other people
  cannot see these tickets unless they copy the file.
- **Opt-in.** Creating a ticket, commenting and filing a bug still need the exact text shown and a yes, as
  with a tracker.
