---
name: diagnosing-bugs
description: Investigates a bug to a stated root cause with an explicit confidence tier, then asks before fixing anything. Runs the instrument, narrow, root-cause loop in any repo with no ticket needed, and also handles a structured bug report from a support team posted in chat. Use when the user hits a bug mid-session — "why is this failing", "this test is red", "CI failed", "a reviewer says this is broken", "debug this", "find the root cause", "investigate this bug", or pastes a support report or thread link. Do NOT use for a monitoring alert or a production outage (use an incident-response skill). Do NOT use to plan a cross-service change (see /to-agent-spec and /build).
user-invocable: true
argument-hint: "[bug description, error, test name, or support thread link]"
---

# Diagnosing Bugs

You are investigating a bug for an engineer. The job is to find the real cause, say how sure you are, and let the user decide what happens next. You are not here to fix fast: a wrong theory acted on has already cost the team time and money.

## Critical — read first

- **Never edit or write a file until the user has seen your diagnosis, with its tier, and said go.** Reading, searching, running read-only commands and read-only queries are always fine without asking.
- **If unsure what to do next, ask. Do not assume.** This holds at every step.
- **State a tier on every diagnosis**, using these labels exactly (align them with your incident-response skill if you have one): **T1 Confirmed** (reproduced, or the evidence is unambiguous), **T2 Probable** (consistent evidence, no surviving competitor, unreproduced), **T3 Candidate** (plausible, unverified; name what would confirm it).
- **Stop after the diagnosis and ask** whether to continue into fix, regression test, cleanup and PR offer. There is no timeout default: silence is not a yes.
- **Never touch the customer-support tool** (<support-desk>). No reads or writes, even if a report's ticket field is filled.
- **Never create, comment on or transition an issue-tracker ticket (or a local `ticket.md`) on your own initiative.** If tickets for support reports are created by an existing automation, leave them alone. If the user asks for a comment on an existing ticket, draft it, show it, and post only on a yes. Reading tickets is fine.
- **Never post to chat without an explicit yes** to the exact draft.
- **Identifiers (record ids, GUIDs) are fine; never copy personal data** (names, emails, phones, government ids, dates of birth, addresses, bank details) into notes, drafts or commits.

## Process

### Step 1 — Take the report and restate it

Work out the entry point:

- **Ad hoc:** a failing test, CI failure, reviewer comment or something the user mentioned. Restate the symptom: expected versus actual, where it was seen, and what is unknown.
- **Support report:** a pasted structured bug report or a thread link (in <support-channel>). **You MUST read references/support-reports.md before parsing the report or touching the thread. Do not improvise the field mapping or the reply format.** If given a link, read the thread with the chat connector. If that tool is absent, say so and ask the user to paste the text.

If the report is ambiguous, ask one focused question before investigating. Only the user can say what they meant.

### Step 2 — Check known footguns

**You MUST read references/known-footguns.md before forming any hypothesis. Do not re-derive a class of bug that is already documented.** If the symptom matches an entry, make it the first hypothesis, and still verify it against the code.

### Step 3 — Investigate, read-only

1. Locate the code path. Read it; do not infer from names. **Say which branch or commit you are reading.** A checkout is often on a feature branch with uncommitted edits. For a production bug read the deployed branch (`git fetch`, then `git show origin/<main-branch>:<path>`), not the working tree.
2. Find what the symptom needs to be true, then list the competing explanations (at least two when you can).
3. Narrow with evidence: git log and blame on the suspect lines, read-only data queries against the affected records for support cases, existing logs and error-tracker faults. Use the tools the project already has.
4. Reproduce when you can without editing files: run an existing test, or a one-off read-only command. A temporary probe or log line is an edit, so ask first.
5. Discard any cause the data contradicts. A cause that only explains part of the symptom is not the cause.
6. **"Flake", "transient" and "external" are diagnoses.** Give them a tier and the evidence that would prove them (earlier green runs of the same job, the same failure on an unrelated branch). A single local pass proves nothing.
7. **Check a data source before putting it in a conclusion.** Confirm the code path actually reads, and something actually writes, the table and column you queried. A column that nothing populates, or a stale synced copy, produces false findings. For queries against the data warehouse or BI tool, **you MUST read references/data-lookups.md first. Do not improvise the database, schemas or privacy rules.**

A timebox from the user ("give it an hour") is a hard limit. At the limit, report what you have.

### Step 4 — Present the diagnosis and ask

Write it in this shape, then ask the user with the interactive question tool (for example `AskUserQuestion`, or plain chat if unavailable):

```
Root cause: [one or two sentences]
Tier: T1 | T2 | T3 — [why]
Evidence: [file:line, query result, test output; branch or commit read]
Blast radius: [how many records or users are affected and how you counted, or "unknown"]
Ruled out: [alternatives and what excluded them]
Not verified: [what you have not checked]
Proposed fix: [what you'd change and where, not yet done]
```

- **T3 after reasonable investigation:** say so plainly, state what is still unknown, and ask how to proceed (dig in a named direction, get data from the user, hand over as is). Never present a guess as confirmed, and never go quiet.
- **Scope doubt:** if the fix needs a second service, a ticket, or is really a build rather than a fix, ask whether to keep going here or switch to the spec/planning skill. Do not decide either way alone.

Options to offer: continue to the fix, change the diagnosis, stop here.

### Step 5 — Fix, only after a yes

1. Make the smallest change that addresses the confirmed cause. Do not widen the fix to adjacent problems; list them instead.
2. Add a regression test that fails without the change when the repo has a test suite for that code.
3. **Verify.** Check for a real local test setup first: a container-compose test service or a documented local test command. List the directory and read the repo's README or task runner; do not assume `<default test command>` works. If a local setup exists and runs, use it. If not (for example specs that run only in CI), syntax-check locally, push on the user's say-so, and watch the CI build. Say which route you took; never skip verification silently.
4. Clean up any probes or scratch files, and look at the diff once before reporting.
5. Offer a commit and PR; do not create either unbidden. Never use `--no-verify` or force-push.

### Step 6 — Support reports only: draft the reply

Draft a reply for the thread covering findings, root cause with tier, fix status, and what the reporter should do next, following `references/support-reports.md`. **Show the draft in chat and send it only when the user says yes to it.** Do not post automatically (unlike an incident-response skill that may reply on its own). If the chat connector is absent, hand over the text and say nothing was sent.

## Examples

- **"the duplicate-reasons spec is failing, why?"** → read the spec and the code, check footguns, narrow to a cause, report "T2 Probable" with evidence, and ask before touching code.
- **Pastes a support bug-report thread link** → reads the thread, parses the template, investigates the affected record ids read-only, states the diagnosis, and after a go-ahead and the fix, shows a drafted thread reply for approval.
- **A bug whose fix spans two services** → reports the diagnosis, then asks: continue here or switch to the spec/planning skill?

## Rules

- No edits before a confirmed diagnosis; ask rather than assume.
- Tier (T1/T2/T3) on every diagnosis; T3 is said plainly.
- Ask before continuing past the diagnosis, and before switching to a planning skill.
- Verify with local tests if they really work, else CI. Never skip silently.
- No customer-support-tool access. No issue-tracker or chat write without showing the text and getting a yes. No personal data.
- Name the branch you read; for production bugs read the deployed code.
- "Flake" and "external" need a tier and evidence like any other cause.
