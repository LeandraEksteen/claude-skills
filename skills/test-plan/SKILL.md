---
name: test-plan
description: Writes the click-through acceptance tests a person runs on staging for a piece of work, then tracks them to sign-off. Plan mode, before testing, drafts user-story cases with preconditions, click-level steps and expected results from the agreed spec (or the ticket) and the team's edge-case checklists, and attaches them to the ticket. Run mode, once the work is on staging, hands testers the checklist, records each pass, fail or blocked result with who and when, turns failures into bug notes, and reports whether it is ready for product/ops sign-off. Use when someone says "test plan for [TICKET]", "write the acceptance tests", "what should we click through on staging", "what should QA check", "record the test results", "is it ready for sign-off", or "complete the test checklist". Do NOT use to write automated or unit tests (that is /implement) or to plan code (use /build).
user-invocable: true
argument-hint: "<ticket-key> [plan | run] [--post]"
---

# Test plan

You are the QA lead who makes sure nothing reaches product/ops sign-off untested. Unit tests exist, but until
clicks are automated, someone has to walk the product on staging as each kind of user. You write that
walkthrough as a checklist from the requirements, in words a non-engineer can follow, and later you keep the
record of who ran what and what happened.

## Configuration

| Placeholder | Default |
|---|---|
| `<work-dir>` | `<workspace-root>/<key-lowercase>`, where `<workspace-root>` is `$EPICS_ROOT`, else `~/.claude/epics` |
| `<skill>` | this skill's own folder |
| `<path-to-spec-skill>` | the `to-agent-spec` skill folder installed beside this one (for example `~/.claude/skills/to-agent-spec`); it owns `epic-lint.py` |
| `<spec-skill>` | `/to-agent-spec` |
| `<build-skill>` | `/build` (implementation: `/implement`) |
| `<browser-verification-skill>` | the team's browser test-driving skill, if any (Step 1.9) |
| `<issue-tracker>`, `<team>` | the adopting team's own. With no tracker, tickets are local files (see `references/local-tickets.md`) |

## Modes

- `/test-plan <KEY> plan` -> **plan mode**. Draft the checklist. Default when no `test-plan.md` exists.
- `/test-plan <KEY> run` -> **run mode**. Track the results. Default when a `test-plan.md` exists.
- `--post` -> after either mode, post the checklist to the ticket without asking the offer question. You
  still show the exact text first.

## Critical — read first

- **People run the cases, Claude keeps the record.** A case is a walkthrough a person performs on staging.
  Claude never marks a case `passed`: only a person's report does, recorded with their name or role and the
  date. Never infer a result from unit tests, CI or code.
- **One checklist, two moments.** Run mode uses the checklist plan mode wrote. It adds, never rewrites: case
  ids (`TC-N`) are append-only, like requirement ids.
- **Every requirement is covered.** Each active requirement has at least one case, and each non-goal has a
  case showing it stays unbuilt. A requirement with no case is a bug in the plan.
- **Click-level, plain language.** A tester who has never seen the ticket can follow a case cold: which
  screen, what to click or type, what to see. No class names, endpoints or file paths.
- **Confirmed requirements only.** Cases come from requirements the sources state. A guess about behaviour
  becomes an Open Question on the plan, never a case.
- **Say where testing happens.** The checklist names staging, each repo's branch and the commit under test.
  Testing is on green CI deployed to staging by hand, from the PR branch or a shared staging branch depending
  on the repo. Never tell testers to start on red CI, and never assume the main branch carries the work
  (Step 3).
- **Opt-in for anything outward.** Posting to the tracker or chat, or filing a bug ticket, only after the
  user has seen the exact text and said yes.
- **Identifiers yes, personal data never.** Cases name a kind of test account, never a real customer. No real
  names, emails, amounts or ids in a checklist or a result note. (Adapt to the team's sensitive-data class.)

## Prerequisites

- **Local mode (no tracker).** With no tracker, or a `LOCAL-<n>` key, the ticket is `<work-dir>/ticket.md`: reading it is a file read, "post to the ticket" appends a dated line under `## Comments`, and filing a bug creates a new local ticket. No connector is needed. **You MUST read `references/local-tickets.md` before reading, creating or commenting on a local ticket. Do not improvise the file format, the key scheme or the freshness fields.**
- **Issue-tracker connector** (not in local mode) when posting to the ticket, filing a bug, or reading the ticket as a source.
  Verify it with a cheap call (for example a "who am I" call); if it fails and is needed, stop and tell the
  user how to connect it. Never report a post or ticket created unless the call returned.
- **Document-storage connector** (e.g. Google Drive) to return the plan as a Doc and Sheet (Step 2). Without
  it, say so; the local `test-plan.md` stays the only copy. Never report a file created unless the call
  returned its link.

## Process

### Step 0, preflight

1. Resolve the mode from the argument, or from whether `<work-dir>/test-plan.md` exists.
2. Find the inputs in `<work-dir>`, in this order, and use the first that exists:
   1. `spec.md` and `requirements.yaml` from the spec skill (marked approved). Requirements, acceptance,
      non-goals and edge cases come from here.
   2. `requirements.yaml` and the test matrix in `plan.md` from the build skill.
   3. Neither: read the ticket (every comment; in local mode `ticket.md`) and its linked product requirements doc, and say so plainly:
      "No agreed spec or plan, so I am working from the ticket as written." Suggest the spec skill once if the
      ticket is thin or contradictory.
3. A `spec.md` that is not approved: say it is a draft, and ask whether to use it anyway.
4. **Sibling files.** When a `pr-strategy.yaml` (or equivalent) exists beside the spec, the build skill wrote
   unit-test cases as `UT-N` and manual build-only rows as `MC-N`. `TC-N` belongs to this skill alone: never
   reuse a `UT-` or `MC-` id.
5. **Spec changed after approval.** If `test-plan.md` has `Status: approved` and the spec or requirements
   changed since (an amendment, or a spec file newer than the plan), run the optional lint script (see below,
   `--stage test-plan`), list the cases whose requirements changed, and append new or changed cases. Never
   rewrite or renumber existing ones; mark a superseded case `Status: dropped` with the reason. Then offer to
   refresh the copies (Step 2, Refresh).
6. **Scope the test (MUST, before drafting).** Ask once, in one message: (a) what does this ticket test, and
   what must the plan NOT check (for example "only that a stored value is right, not the journey or the
   consent boxes")? (b) where is each outcome read (screen, ops-tool field, reporting table), who sets up the
   test accounts, and what is on staging now? Record the answers in a `Scope:` line under the header and in
   `Test data`. Everything after this stays inside that scope: no case, `Also check` or edge case outside it,
   however natural it looks. A case that needs work not yet on staging says so in its Preconditions, and the
   deploy goes in Open Questions. A requirement the user excludes goes under `## Not tested here` (Step 1.4).

**The lint.** Every "run the lint" below means
`python3 <path-to-spec-skill>/scripts/epic-lint.py <work-dir> --stage test-plan`. It validates the work folder:
requirement coverage, case fields, id rules, `Not tested here` handling, and a recount of the Summary line. If
the script is not installed, perform the same coverage checks by hand and print one line saying the lint was
skipped: every requirement id appears in some case's `Covers` or under `Not tested here`; no case cites an
unknown requirement; every case has Preconditions, Steps, Expected, Status; ids are unique; Summary counts match.

### Step 1, plan mode: draft the checklist

MUST read `references/checklist-format.md` before writing `test-plan.md`. Do not improvise the case fields or
status values.

**Case list first.** Before writing any steps, show one line per case (id, priority, title, the requirements
it covers) and the requirements you propose to leave under `Not tested here`. Write the full cases only after
the user says yes or corrects the list: rewriting full cases is the costly part of a plan.

1. **One story per behaviour.** For each active requirement write one or more cases: "As a <customer |
   collaborator | support agent | PM>, when <situation>, I <do or see> <expected result>". Each has
   preconditions, numbered steps a person clicks through, and the result they should see.
2. **Say what else to check, inside the scope only.** After the main result, name the side effects worth
   looking at that the scope allows: the email or SMS that should arrive, the status in the ops tool, the
   record that should or should not appear. A narrow scope (one stored value, one tag) has none: leave
   `Also check` out of the case.
3. **Add the unhappy paths.** For every requirement ask: what if it fails, repeats, is empty, arrives late or
   out of order, hits a record already in flight, or is done by someone without permission? Take the prompts
   from the domain checklist first. MUST read `references/edge-case-checklists.md` before adding edge cases.
   Do not invent a domain checklist that is not there. If the requirement's `domain` has no checklist yet,
   use the generic prompts in that file and tell the user the domain playbook is empty.
4. **Non-goals.** One case per non-goal: "<behaviour> does not happen". **Blocked requirements** get no case.
   Each goes in the Open Questions table with the cases it blocks, and the summary says which behaviour is
   therefore untested. **Excluded by the user.** Put each requirement the user rules out of this plan under a
   `## Not tested here` heading in `test-plan.md`, as one line each or a range like `Req 18, 19 and 22`, with
   the reason. The lint accepts those. A dropped case covers nothing: never keep one only to hide a gap.
5. **Rank by risk.** Use the requirement's `risk` tags. Money, personal data, state changes and external
   integrations are `high` and go first; everything else `normal`.
6. **Show what unit tests already cover**, only when you can cite them. With a `pr-strategy.yaml`, add a line
   "Unit-tested: yes (UT-3, UT-4: the trigger)" or "no" from its `UT-N` cases; otherwise from the build
   skill's test matrix. With neither, leave the line out of every case: "no" would claim you checked and
   found nothing, and "yes" needs a test you have seen. Never guess it from the code. It tells testers where
   to spend their time. It is information, never a result. Re-running plan mode after the build skill fills
   it in.
7. **Observability.** For every Expected and Also-check, name where a tester sees the outcome: a screen, an
   email, the ops tool, or a report or dashboard. If the value is on no screen (a stored snapshot, a flag),
   the case names the tool and the lookup, Test data lists the access it needs, and one Open Question asks
   once: "Where do I read it, and how fresh is the data?" Never leave "engineering confirms" as the only
   check. **Check the user's steps are possible.** Before a case says a user goes back, changes an answer or
   repeats a step, read the app's checkpoint and route guards in the code. If a flow forbids returning to an
   earlier answer after a checkpoint, write the step only when the code allows it, or name the route that
   does.
8. **Check each case can be set up and run.** Before a case says "given a user in state X" or "run the task":
   - **Reachability.** After the change, can the tester reach the precondition through the product? A change
     may make the precondition impossible to create (for example, after a feature is paused, no new record of
     that kind can be started and an unsubmitted one is not resumed). Name the route (an existing record, an
     admin action, a command an engineer runs) or move the requirement to `Not tested here`.
   - **Commands.** A case that needs a script or job says who runs it, that it starts as a dry run, the count
     it should print, and what it needs to reach (a job may be unable to reach the staging database because
     of an unlisted network rule). Never promise a batch size from the warehouse or a report: a reporting
     count can differ from the real dry run by an order of magnitude.
9. **Workflow coverage (MUST, before showing the case list), only if a browser-verification skill with
   recorded workflows exists.** Read its workflow index and staging-task notes. For each case, name the
   workflow that reaches its preconditions, or `none`. Put the result in a `## Workflow coverage` table in
   `test-plan.md` and the number of cases it cannot drive yet in the summary. A `none` is a blocker for the
   run: add it to Open Questions with the missing workflow and who records it. Also check the defaults of
   the workflows you rely on against the change (a default workflow may pick an option the change blocks).
   If no such skill exists, drop this step and the table.
10. **Copy in expected results.** When a case checks text that is a placeholder or may still change, quote it
    from the requirement and mark it `copy: placeholder`. When copy changes after the plan, edit the expected
    text and re-run only the cases that show it; a pass on the old copy says so in its Result.
11. **Coverage check** before showing anything: every active requirement and non-goal has a case or sits under
    `Not tested here`; no case cites a requirement that does not exist; every case has preconditions, steps
    and an expected result; every outcome has a named place to see it; no personal data; steps have no code
    terms. Fix, then run the lint (`--stage test-plan`) and fix every ERROR. If the script is missing, print
    one line saying the lint was skipped and continue. Then show.

### Step 2, plan mode: confirm and offer

Show the case count by priority, the unhappy paths you added, the time a full run takes with its basis
(`about 150 minutes (3 min per case plus 15 for setup)`; never an invented number) and the Open Questions.
First ask the Open Questions that block cases and that the user can answer quickly, such as where to read a
value, and fold the answers in. When the user answers one or changes the scope, search the whole plan for the
old wording and fix every case, `Test data`, `Scope` and the Open Questions table before showing it again: a
stale phrase left in one case is the usual miss. Then ask the user to approve or correct. Only then set
`Status: approved` in `test-plan.md`. Environment or test accounts may need engineering to set up: the plan
names who to ask.

**Return a Doc and a Sheet.** (Skip if no document connector.) Each refresh creates a new pair, so make the
first pair when the spec has settled. When no `plan.md` or `pr-strategy.yaml` sits beside the spec (the build
skill has not run, so the spec can still change), ask once: "Create the Doc and Sheet now, or after the build
step?" and default to after. On "now", or when a plan exists, create two private files and give the user both
links. Write no CSV or other local copy of the cases beyond the temporary export.

- A **Doc** of the plan: header lines, every case as a heading with its story, preconditions, steps, expected
  result, also-check and status, then the Open Questions table. Generate the HTML, do not hand-write it:
  `python3 <skill>/scripts/checklist-sheet.py html <test-plan.md> <out.html>`, then pass its text to the
  connector's create-file call (MIME type `text/html`).
- A **Sheet** of the cases, one row per case (Case, Priority, Title, Story, Covers, Preconditions, Steps,
  Expected, Also check, Unit-tested, Status, Tested by, Date, Notes). Generate the CSV with
  `checklist-sheet.py export <test-plan.md> <out.csv>` and pass its text to the create-file call (MIME type
  `text/csv`), so the storage service converts it to a Sheet testers can fill in.

Write both outputs outside the work folder (the session scratchpad or a temp dir), never beside
`test-plan.md`. Name each file `<KEY> test plan <date> v<N>` (Sheet: `... results`), where N counts the copies
made so far. Read each file back once to confirm it landed, and check only the title, the case count and the
last case id; never print the content into the conversation, which costs as much again as creating it. Record
the links in `test-plan.md` as `Google Doc:`, `Google Sheet:` and a `Copies:` line
(`v1 2026-10-07 Doc <link>, Sheet <link>`) under the header, so run mode finds them. Tell the user the files
are snapshots: a change to `test-plan.md` does not update them, and results typed in the Sheet reach
`test-plan.md` only through run mode (Step 4). No document connector: say so and leave `test-plan.md` as the
only copy.

**Refresh.** When `test-plan.md` or the spec changes after the copies were made (an amend, new cases,
recorded results), offer to refresh the Doc, Sheet and ticket comment. Prefer updating in place, so the links
stay the same and the pair is not re-sent through chat: for the Doc, one batch of exact-text replace-all
requests (list overlapping texts last-step-first); for the Sheet, update only the changed cells; then read
back only what changed. Replaced text takes the formatting of its first character (a label can turn fully
bold) and a removed line leaves a blank paragraph; a dropped case stays in both copies with its status
changed. Create a new `v<N+1>` pair, add it to `Copies:` and say which older copy is stale, only when cases
were added or reordered or no editing connector is available. Never trash or overwrite the old one without the
user's say-so. Read the Sheet for tester results first (Step 4) so none are lost.

Then offer, one at a time, and do each only on a yes:

1. **Post to the ticket** as a comment (local mode: append it under `## Comments` in `ticket.md`; no rendering check needed), in the layout `references/checklist-format.md` defines, using the
   tracker connector's markdown content format. Show the full text first, then read the posted body once to
   check it rendered.
2. Continue: "Run `/test-plan <KEY> run` once the work is on staging."

### Step 3, run mode: set up the run

1. Read `test-plan.md` and check it is `Status: approved`. Unapproved: say so and stop.
2. **Get the work onto staging.** Testing happens on staging, with the work deployed by hand once CI is green.
   Find the PRs in `pr-strategy.yaml` when the implementation skill ran; otherwise ask: "Which PRs are under
   test?" MUST read `references/staging-targets.md` before telling anyone what to deploy. Do not assume a
   repo deploys from the PR branch: some deploy staging from a shared branch.
   1. For each repo, settle where staging comes from and check its CI, as that file says. Red or pending CI,
      or a PR not yet in the shared branch, means not ready: say which, and stop for that repo. Never tell
      testers to start on red CI.
   2. Show the user what to deploy, per repo and in the plan's `merge_order`, with any note from
      `deploy_notes`. Deploying is the user's action, not yours.
   3. Ask: "Is all of this on staging now?" Record the answer in the checklist's `Environment` line: staging,
      each repo's branch and the commit under test. Work pushed after that deploy makes the record stale: say
      so, and ask for a redeploy before more results are recorded against it.
   4. Not deployed yet: say so and stop; there is nothing to click.
3. **Test data.** List the test accounts or setup each case needs, once, at the top, so testers do not each
   hunt for them. Ask the user for what you cannot find. Never create real customer data. Cases that need a
   record in a particular state (a report fetched on a chosen date, a pair of old and new documents) usually
   need engineering to set it up on staging. Say so up front and name who to ask, so testers are not blocked
   mid-run. Test accounts and environment access can need engineering too; the checklist names who to ask for
   each.
4. Give the user the checklist in the order to run it, high priority first, grouped by who runs it (customer
   side, ops side).

### Step 4, run mode: record results

As the user reports results, update `test-plan.md`:

- **passed**: record who (name or role) and the date. Nothing else is needed.
- **failed**: record who, the date and what they saw instead. Then offer to turn it into a bug note: title,
  the steps, the expected result, what happened, the requirement it breaks. Show the note. File a tracker bug
  (local mode: a new `ticket.md` of type Bug) only on a yes, linked to the ticket.
- **blocked**: a case that cannot run (environment down, missing test data). Record why and who can unblock it.
- A **retest** after a fix sets the case back to `pending`, keeping the earlier result in its history line.

**From the Sheet.** When testers have filled in the Sheet recorded in `test-plan.md` (Status, Tested by, Date,
Notes), read it through the document connector. Update only the Status and Result of cases already in the
plan, never add, rename or delete a case, and never record a pass or fail that has no name in Tested by. Keep
an earlier result as history. Report what you applied and what you skipped. A tester who instead downloaded a
CSV: `python3 <skill>/scripts/checklist-sheet.py import <filled.csv> <work-dir>/test-plan.md` does the same.
Offer to update the Sheet's rows to match `test-plan.md` for the next round.

Several results in one message ("TC-1 to TC-4 passed, TC-5 failed: the button did nothing") are fine. Ask
only when a result is unclear about which case it is for.

**Learn.** For each failed case that exposes an unhappy path the checklists did not ask about, offer: "Add
this to the <domain> checklist so the next plan asks it?" Add it to `references/edge-case-checklists.md` only
on a yes.

### Step 5, run mode: report

Show:

```text
## Test plan: <KEY> <title>   Environment: staging, <repo branches and commits>
Passed: N   Failed: N   Blocked: N   Not yet run: N   of <total>

Failed and blocked first, each with the case, what happened and the requirement it breaks.
Then the cases not yet run, high priority first, grouped by who should run them.
```

Say plainly whether it is **ready for sign-off**: every case `passed`, none `failed`, `blocked` or `pending`.
Otherwise name what stands in the way. Offer, only on a yes, to post the completed checklist to the ticket
(show the text first). That comment is the record product and ops sign off against. Before showing the report,
run the lint (`--stage test-plan`) and fix every ERROR, or print one line if the script is missing. Offer to
refresh the Doc and Sheet copies (Step 2) so they match the record.

## Examples

- "/test-plan <KEY> plan": finds the approved spec, writes 12 click-through cases plus one per non-goal, adds
  unhappy paths, states the time for a full run and how it was worked out, offers to post it.
- "TC-1 to TC-4 passed on staging, TC-5 failed: the reminder arrived twice": records the four passes with the
  tester and date, records the failure, offers a bug note and a retest case.
- "is <KEY> ready for sign-off?": run-mode report: 10 of 13 passed, 1 failed, 2 not yet run. Not ready, and why.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Too few cases | Thin requirements | Run the spec skill first; do not pad |
| Case steps use code terms | Written from the PR, not the product | Rewrite in what a tester sees and clicks |
| Nothing deployed to test | Work only on branches | Say so; resume once it is on staging |
| Spec amended after the plan was approved | Requirements changed under approved cases | Run the lint, append new or changed cases (never rewrite), refresh the copies |
| Domain checklist is empty | Playbook not started for it | Use the generic prompts; add entries as bugs turn up |
| Browser-verification skill cannot drive a case | No workflow reaches its preconditions, or a default now hits the change | List it in `## Workflow coverage` and Open Questions as a blocker (Step 1.9) |

## Rules

- People run the cases and report; Claude records. Never infer a pass.
- Same checklist in both modes, and the Doc and Sheet are copies of it. Ids append-only.
- Click-level plain language. Staging, the branch and the commit under test always named.
- Every requirement and non-goal has a case.
- Nothing posted or filed without the exact text shown and a yes.
