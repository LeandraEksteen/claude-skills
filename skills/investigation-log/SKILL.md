---
name: investigation-log
description: Keeps a long-running, multi-session investigation cheap and consistent. A small INDEX.md holds the goal, decisions, parked items, open questions, in-flight forks and a compaction-safe STATE block; per-topic files hold labelled findings; an append-only log holds history. Use when starting or resuming an investigation, before a /compact, when forking a side session, when a notes file has grown too big to re-read, or when syncing findings to a shared doc — "start an investigation", "resume the investigation", "checkpoint before I compact", "write a fork prompt for a side session", "split these notes up", "sync the findings doc", "what did we decide so far". Do NOT use to hand a summary to a person, to turn sources into a build spec, to root-cause one bug, or for a production incident.
user-invocable: true
argument-hint: "<start|resume|checkpoint|fork|migrate|doc-sync> [slug]"
---

# Investigation Log

You keep a long investigation cheap to resume. State lives in files, not in the conversation: after a
compaction, a fork or a new day, read one small index and carry on. Default root:
`<investigations-root>/<slug>/` (configurable; keep it outside any repo). If the user already has notes elsewhere, use that folder and say so.

## Critical — read first

- **On start or resume, read ONLY `INDEX.md`.** Never read `log.md` in full. Search it with `grep`. Open at
  most one topic file per question, and only when the question needs it.
- **Say what you loaded**, in one line: slug, STATE, counts of open questions and in-flight forks.
- **Label every claim**: `verified` (with a pointer and date), `inferred`, or `proposal`. A claim read by an
  agent, taken from a vendor page, or taken from meeting notes is `inferred` until you check the primary
  source yourself. Never promote it quietly.
- **The shared doc is for sharing, the notes are for working.** Edit only what the user asked. Ask before
  adding a section. Keep commentary about rejected sources out of the doc and topic files; put it in the log.
- **Never send, post or share anything.** Draft only. Fork prompts and doc text are drafts for the user.
- **Propose before restructuring.** `migrate` is propose-only until the user approves.
- **You cannot run `/compact`.** Update STATE, then tell the user to run it.
- **Memory holds a pointer, never a copy** of the index.
- No personal data: identifiers are fine; names, emails, dates of birth and addresses are not. (Adapt this
  line to the team's sensitive-data class.)

## Process

**Step 1, pick the mode.** Take the mode from the argument or from the request. `start` for a new
investigation, `resume` for an existing one, otherwise `checkpoint`, `fork`, `migrate` or `doc-sync`. No slug
given: `ls` the root and ask which one. Never guess between two.

**Step 2, start / resume.** MUST read `references/layout-and-index-template.md` before creating or editing
`INDEX.md`; do not improvise sections or the STATE block.
- `start`: ask for the goal and constraints, create the folder from the template, add the memory pointer
  (Step 8), append the first log entry.
- `resume`: read `INDEX.md` only. Report the one-line summary from Critical. Run
  `python3 scripts/check-index.py <folder>`: if it reports `state-stale` (STATE older than the last log
  entry), say so and offer a checkpoint before doing anything else.

**Step 3, record findings.** Findings go in `topics/<area>.md`, one file per area, each claim labelled. MUST
read `references/evidence-labels.md` before writing any finding; do not invent label wording. Append a dated
one-line entry to `log.md` for each notable step (what was read, what changed, what was corrected). Update
INDEX decisions, parked items and open questions when they change.

**Step 4, checkpoint.** At a natural milestone, and always before the user types `/compact`, rewrite the
STATE block. Milestones: a fork registered or finished, a doc edit done, a decision recorded, or five log
entries since the last STATE. STATE is at most 10 lines: where we are, the next step, what is in flight,
what not to redo. Append a log entry. If the user is about to compact, finish with: "STATE saved. Run
`/compact` now."

**Step 5, fork.** MUST read `references/fork-prompt-template.md` before drafting a side-session prompt; do
not improvise the prompt or output contract. Fill the template with paths (never pasted content), write it to
`forks/<name>-prompt.md`, register it in the INDEX Forks table (name, prompt path, output path, status), and
show it to the user to start. If the user starts forks as task chips (spawned side tasks), the chip prompt is
the filled template (paths, not pasted content). When the user starts the fork, set it to `running`; when its
output file exists, read it and set it to `done`, then fold the labelled findings into the topic files.

**Step 6, migrate.** MUST read `references/migration.md` before proposing a split of an existing notes file.
Do not move or rewrite anything before the user approves the proposal.

**Step 7, doc-sync.** MUST read `references/doc-sync.md` before editing a shared findings doc.

**Step 8, memory pointer and token discipline.** MUST read `references/memory-and-tokens.md` before writing
the memory entry or launching fan-out agents.

## Examples

- "resume the X investigation" -> read INDEX.md only; "Loaded X: STATE 2026-10-09, 12 open questions, 2
  forks running." Open a topic file only when asked about it.
- "I'm about to compact" -> rewrite STATE, append a log line, say "Run /compact now."
- "fork a side session to review the masking approach" -> fill the fork template with paths and the output
  file, register it in INDEX, show the prompt.
- "this notes file is 700 lines, fix it" -> `migrate` in propose-only mode; wait for approval.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| INDEX.md over about 100 lines | detail leaked in | move it to a topic file; keep a one-line pointer |
| A claim has no label | written from memory of an agent report | label it `inferred` and add the basis |
| Fork output contradicts a verified claim | fork read a stale source | log it, re-check the primary source, relabel |
| Doc and topic files disagree | doc edited without sync | check the section map in INDEX, fix the topic file or ask |

## Rules

- Index first, one topic file at most, grep the log.
- Every claim labelled; agent and vendor reads stay `inferred` until you verify them.
- Doc edits: only what was asked; ask before new sections.
- Propose before migrating; draft, never send; tell the user to run `/compact`.
- Memory is a pointer to INDEX.md.
- Context past about 300k tokens: checkpoint and ask for `/compact`.
- Related skills (map handoff and retro to the team's equivalents): handoff (person-facing summary, reads INDEX.md), /to-agent-spec
  (spec from this investigation's decisions), retro skill (harness improvements, not investigation state).
