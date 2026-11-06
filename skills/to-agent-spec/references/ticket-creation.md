# Creating the ticket

Loaded by **Step 5** when creating a ticket, and by **Step 1** for the Freshness section. Ticket creation only happens when the work has no ticket and the user said yes to creating one. A separate ticket-writing skill (`<ticket-skill>`) writes, previews and files the ticket; this file says what to hand it and what to do afterwards. If you have no such skill, include its job here: draft in the team's usual structure, show the full draft, and file only on a yes.

## Local mode

With no tracker there is no ticket skill. Build the ticket from the field list below, show the full text, and on a yes write `ticket.md` as `references/local-tickets.md` describes. The "After the ticket exists" steps still apply, with the local key and folder name.

## Hand off to the ticket skill

Run it with the spec as its source. Do not draft the ticket here, and do not pick the project, issue type or layout yourself: the ticket skill owns them. Pass:

- **Type:** Bug when the spec fixes wrong behaviour, otherwise Task/Story. One ticket by default. If the spec has several independent outcomes, offer the user the ticket skill's tree mode (one epic with tasks under it); never use it unasked.
- **Context:** the goal and why, as in `spec.md`.
- **Scope** and **Not in scope**, as in `spec.md`.
- **Acceptance criteria:** one checkable line per active requirement, the `Req #` first.
- **Edge cases and failure behaviour**, and **open questions** with who decides each. Blocked requirements stay visible in the open questions.
- **Sources:** links to the PRD, chat threads and tickets read, plus "Spec: `<workspace-root>/<name>/spec.md` (local to <the user>)" so the author can find it.

No names, emails or amounts from real customers. The ticket skill shows the full draft and files it only on a yes. If it cannot reach the tracker or the user says no, stop and report that nothing was created.

## After the ticket exists

The ticket skill returns the key. Then:

1. Rename `<workspace-root>/<name>/` to `<workspace-root>/<key-lowercase>/`.
2. In `requirements.yaml` set `key`, `jira_updated` and `jira_content_sha` (see Freshness; field names may be renamed for your tracker, but `scripts/epic-lint.py` uses the names shown), and write `state/<tracker>-snapshot.md`.
3. In `spec.md` set the title's key, and add the ticket to "Sources read".
4. Report the key and link. Do not transition, assign or link other issues unless asked.

## Freshness

Used here and by Step 1 for an existing ticket. The ticket's `updated` timestamp changes on a mere comment, so the planner must compare content, not the timestamp.

- `state/<tracker>-snapshot.md`: the summary, the sha256 of the description text, the ids of the comments read, and the date read.
- `requirements.yaml`, optional field: `jira_content_sha: <sha256 hex of summary + "\n" + description>` (the description text as the API returns it).
- Set `jira_updated` AFTER adding any comment you post to the ticket, so your own comment does not look like someone else's change. Recompute both fields after any edit to the ticket.

Compute the hash with: `python3 -c "import hashlib,sys; print(hashlib.sha256((sys.argv[1]+'\n'+sys.argv[2]).encode()).hexdigest())" "$SUMMARY" "$DESCRIPTION"`.
