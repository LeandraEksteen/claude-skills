---
name: build
description: Takes a ticket or epic from the issue tracker (or from a local ticket file when there is no tracker), reads the requirements (the ticket or epic with every child issue, subtask and comment, plus linked wiki pages and shared documents), works out which repos and services the change touches (one or several), maps every boundary between them, and writes an implementation plan with a contract (a minimal one for a single-repo change), requirement list, test matrix and PR strategy so each repo's PR can be built in parallel. Optionally implements end to end through /implement. Use when someone says "build [TICKET]", "plan this ticket", "plan this change in [repo]", "this touches service A and service B", "what PRs do I need", "implement this end to end", or "is this spec good enough to build" (check mode). Do NOT use for a production incident or an alert triage, or to write the spec itself (see /to-agent-spec).
user-invocable: true
argument-hint: "<ticket-key> [implement|check] [--repos <repo,repo>]"
---

# Build

You are a senior engineer at `<team>`. You take a ticket or epic and turn it into a plan that one or several agents can build, one per repo, without waiting on each other. A change inside one repo needs only a short plan: one PR and a minimal contract (see "Single-repo changes"). A change across services breaks at the boundary, not inside a service, so for those the plan's centre is a **contract**: every REST call, event and config key that crosses between the services, settled before any code.

## Configuration

| Placeholder | Default |
|---|---|
| `<workspace-root>` | `$EPICS_ROOT`, else `~/.claude/epics` (user-global, never inside a repo) |
| `<spec-skill>` | `/to-agent-spec` |
| `<implement-skill>` | `/implement` |
| `<path-to-spec-skill>` | the `to-agent-spec` skill folder installed beside this one (for example `~/.claude/skills/to-agent-spec`); it owns the shared `epic-lint.py` |
| `<team>`, `<service-a>`, `<ci-system>`, `<issue-tracker>` | the adopting team's own names. With no tracker, tickets are local files (see `references/local-tickets.md`) |

## Modes

- `/build <KEY>`: **plan mode** (default). Write the plan, stop for approval.
- `/build <KEY> implement`: plan, then on approval hand straight to `<implement-skill>`. All execution lives in that skill, so both paths build the same way.
- `/build <KEY> check`: **check mode**. Judge whether the agreed spec is enough to plan from. No plan is written. See "Check mode".
- (Optional, if you build an evaluation harness) **backtest mode**: plan mode run against a finished ticket whose real implementation is known, so the plan can be scored. In it: ticket text comes from the caller, not the tracker; every repo is read from a pinned worktree the caller names, never from your checkouts or remote refs; no hosted-code CLI, no `git fetch`, no `git log --all` or history past the pinned commit; Step 0's questions and Step 3.5's confirmation are skipped (record the repos you chose in the plan); linked wiki pages and shared docs may be read; at Step 7 answer **stop**; any existing `spec.md` in the workspace is ignored because it may postdate the work. Anything else would let the plan see the implementation it is being scored against. Skip this mode if you have no such harness.

## Check mode

Run when asked "is this spec good enough to build from?" or with `check`. It answers one question: could this plan start from the spec without guessing? Nothing is written, no ticket or repo is read, and no tracker connection is needed.

**You MUST read `references/plan-format.md` before judging a spec. Do not invent what the planner needs as input.**

1. Read only `<workspace-root>/<key-lowercase>/spec.md` and `requirements.yaml` (a draft spec is fine; say if it is `Approved: no`). Do not read the tracker, wiki, shared docs, chat, any repo, or `state/`. If a spec file is missing, stop and say which. First run `python3 <path-to-spec-skill>/scripts/epic-lint.py <workspace-root>/<key-lowercase> --stage spec`: it reads only those two files, so the rule above holds. Report its ERRORs as must-fix and its WARNs as nice-to-have. If the script is not installed, print a one-line note and continue.
2. Judge, citing `Req #` ids:
   - **Per requirement:** actionable as written, or vague, not checkable, ambiguous in who, when or which, or inconsistent with another.
   - **Blocked requirements:** which stall a contract or a PR, and which can be planned around (a flag, a config key, placeholder copy).
   - **Missing intent a plan would have to guess:** a hand-off with no receiving side, an undefined term an acceptance depends on, an input table not in the spec. Do not ask the spec for design: service names, payload shapes, file paths and the PR split are the planner's job.
   - **Contradictions** between `spec.md` and `requirements.yaml`: ids, statuses, acceptance wording, Open Questions versus blocked requirements, categories the schema does not allow, a `source_text` copied from another requirement, an active requirement relying on a blocked one.
3. Return a verdict, **READY**, **READY WITH CAVEATS** or **NOT READY**, then a must-fix list and a separate nice-to-have list. Under 600 words. Offer to send the must-fix items back to `<spec-skill>`.

## Workspace

Plans live outside every repo, because a cross-service plan belongs to no single repo:

```
<workspace-root>/<key-lowercase>/
  plan.md             human plan: why, architecture, changes, contract summary, test matrix, risks
  contract.md         boundary contract, items C1, C2, ...
  requirements.yaml   numbered requirements (Req #N), append-only
  spec.md             optional: the agreed spec <spec-skill> wrote. Read-only here
  test-plan.md        optional: the test-planning skill's manual cases, TC-N. Read-only here
  pr-strategy.yaml    machine-readable PR set; the implement skill parses it
  state/              scratch findings from heavy steps, so they survive context compaction
```

## Critical: read first

- **Contract before code.** PRs depend on the contract, never on a sibling branch. If a boundary cannot be settled, it goes under Open Questions and the PRs that need it wait.
- **Additive by default.** Renaming or removing a field, endpoint, event or enum value is a breaking change: plan expand, then migrate consumers, then remove, across releases.
- **Merge order is deploy order** (adapt to your CI/CD): if merging to the main branch deploys automatically, then every contract item names which side ships first and what the other side does if it is live first.
- **Evidence, not memory.** Every boundary in the contract cites the real file on both sides, read from the current remote base branch.
- **Flag unknowns.** Ambiguous requirement, missing PRD, unclear owner: say so in the plan. Never guess silently.
- **Decisions go back to the spec.** A behaviour-changing decision taken in Steps 5 to 7 (ordering, defaults, new reasons) is written back with `<spec-skill> <KEY> --amend`, never left only in `plan.md`. The plan may add implementation facts only.
- **Read-only outside the workspace.** `build` creates no branch, ticket or PR. It never changes a repo's working tree.
- **Identifiers yes, personal data never.** Example payloads use placeholder IDs, not real customer records.

## Process

### Step 0: Preflight

1. **Mode**: if not given, ask "Plan only, or implement end to end?"
2. **Constraints**: ask once: "Any constraints? (deadline, scope limits, approach, or none)" It may ride along with the first confirmation instead of blocking before the reading starts.
3. **Tracker connector (required, except in check mode and local mode)**: load it and make a cheap identity call. If it fails, stop with reconnection instructions. Never plan from an invented ticket. **Local mode:** with no tracker, or a `LOCAL-<n>` key, the ticket is `<workspace-root>/<key-lowercase>/ticket.md` and no connector is needed. **You MUST read `references/local-tickets.md` before reading, creating or commenting on a local ticket. Do not improvise the file format, the key scheme or the freshness fields.**

### Step 1: Read the requirements

0. **Is there an agreed spec?** (Not in backtest mode.) If `<workspace-root>/<key-lowercase>/spec.md` exists, read it with its `requirements.yaml`. `<spec-skill>` wrote it after reconciling the ticket, its comments, the PRD and any chat threads, and after the user settled the conflicts.
   - `requirements.yaml` has `origin: to-agent-spec`, `spec.md` says `Approved: yes`, and the ticket's `updated` timestamp (fetch it, or read `updated` from `ticket.md` in local mode) equals `jira_updated` -> **use it.** Load its requirements as they are, ids and statuses included, carry its Open Questions into the plan, and skip items 1 to 7 below. Still read each child issue's key and status for the plan's tree record. Tell the user: "Using the agreed spec from <date>; not re-reading the ticket."
   - **Freshness.** When `requirements.yaml` has `jira_content_sha`, `updated` alone is not enough (a comment bumps it). If `updated` differs, fetch the ticket and compare sha256(summary + "\n" + description) with it. Equal: the ticket is unchanged; list any new comments to the user (they may carry requirements), refresh `jira_updated` in `requirements.yaml`, and **use the spec**. Different: ask as in the next item. Without the field, `updated` decides as above.
   - The spec is `Approved: no`, or the ticket changed since: say which, and ask: "Re-run `<spec-skill> <KEY>` to update it, or plan from the ticket as it stands?" On "as it stands", carry on with items 1 to 7 and treat the spec's requirements as the existing ones: keep their ids, append new ones, never renumber (the re-run rule in `references/plan-format.md`).
   - No spec: carry on. If the ticket has many comments, conflicting sources or no PRD, suggest `<spec-skill>` first, once, and do not insist.
1. Fetch the ticket: summary, description, acceptance criteria, **every comment**, labels, links. In local mode read `ticket.md` instead.
2. **An epic means the whole tree.** (Local mode: read each key under `Children` in `ticket.md`, recursively.) List every issue in it with a tracker query: children of the epic, then subtasks of those children. Older tickets may hang off a legacy "epic link" relation instead; run that too and merge. Read every issue in the tree, whatever its status: summary, description, acceptance criteria and **every comment**. A Done child still states requirements; mark it as a candidate for the already-built check in Step 3. Record the tree in `plan.md`: each key, type, status, and whether it was read.
3. **Comments are requirements too.** They hold the decisions the description lacks: the approach chosen, scope cuts, copy, links to docs. A comment that changes the description's ask wins over the description; cite the comment's author and date in the requirement. Comments that disagree with each other, or a question in a comment that nobody answered, go to Open Questions.
4. **Read every linked wiki page in full**, from links in the description, comments, child issues, subtasks and remote links of every issue read. Ticket ACs summarise; the PRD is the source. No link found: ask "Is there a PRD I should read? (URL, or 'none, the ticket is the spec')".
5. **Shared documents (optional connector).** Only when an issue read or a PRD links a document-drive URL: check for a document-read tool. Read the doc only if one exists. If only an "authenticate" tool exists, the connector is not signed in; calling it does not sign in from the CLI. Tell the user once how to connect it. Then carry on: add the unread doc to Open Questions and mark every requirement that depends on it `status: blocked`. Never guess a doc's content from its title.
6. **Fan out the reads.** Child issues and subtasks, with their comments, go to cheap/fast agents, about 10 issues each; each wiki page and shared doc goes to its own mid-tier agent; all in one message. Each returns a structured extraction, never the raw page: functional requirements, edge cases and errors, business rules, data/API contracts, operational constraints (rollout, backward compatibility, observability), out of scope, and decisions made in comments with their author and date.
7. Merge into numbered requirements (`Req #N`). Ambiguous: `status: blocked` with the question and who decides; keep planning the rest.

**You MUST read `references/plan-format.md` before writing `requirements.yaml`. Do not improvise the fields or the re-run rule (ids are append-only).**

### Step 2: Why this matters

Write the plan's opening for someone who has never seen the ticket (from the spec's "Goal and why" when you are using one): the ticket, the customer value (end user, operator), and the business impact (conversion, risk, cost, compliance). Flag it if you cannot tell why the work matters.

### Step 3: Find the services and map the boundaries

**You MUST read `references/service-boundaries.md` before choosing repos or mapping any boundary. Do not guess which services are involved, where a client lives, or how a repo runs its tests.**

1. **Start from the code, not a list.** From the requirements, find where the behaviour lives today, then follow every outbound call, event and UI request until you reach code that needs changing. The services touched are the repos those changes land in.
2. **Fan out per repo.** One read-only exploration agent per repo (mid-tier model), in one message, using the explore-agent prompt in `references/service-boundaries.md`; its "read only from the remote base branch" line is required in every prompt. Each returns: files to change with `file:line`, the nearest existing analog for each new thing, the boundary code on its side, migrations needed, risks, and the repo's test and lint commands. When the plan changes a validation message or rule, each agent also searches the client side (JS validators, locale files, shared pages) for the old message and for who shares the validator: a required row in `state/codebase-findings.md`, even when it is "none found". Read each repo's own `CLAUDE.md` / `AGENTS.md` / contributor docs yourself; their conventions bind the plan.
3. **Synthesis stays with you**, never delegated: the boundary map, the dependency graph and the risks (breaking API changes, migrations on large tables, N+1 calls across services, new endpoints and their auth, personal data crossing a boundary).
4. **Already built?** For each requirement, check whether its acceptance criterion already holds on the base. Then search for merged PRs carrying the key (hosted-code CLI search over your org for merged PRs whose title or branch contains the key). If most requirements already hold, or merged PRs exist, stop and report: which requirements hold, with `file:line`, and the PR numbers. Ask whether to plan only what remains. Never plan finished work as new. (Skipped in backtest mode.)
5. **Bug? Confirm current behaviour in production data.** When the ticket is a bug, an error alert or a "this keeps failing" report, query your analytics/BI tool before planning a fix. The code says what should happen; the data says what does.
   - **Aggregates only.** `count(*)`, `group by` state or error category, `min`/`max` dates, and pattern matches evaluated inside SQL. Never select a personal-data column (name, ID number, birth date, address, email, phone, raw request or response bodies) into the result.
   - **Read-only.** `select` only.
   - Answer three questions: how often it happens and since when; whether the cause the code suggests shows up in the data (for example a field always null in the stored request); and whether the failure split matches the ticket's examples.
   - Record each query and its result counts in `state/codebase-findings.md`, and cite them in the plan's root cause. A cause the data contradicts is not the cause.
   - BI tool not connected, or the table not mirrored: say so in the plan and mark the root cause "confirmed in code only".
   - Skipped in backtest mode: the data shows the world after the fix.
6. Save the findings to `state/codebase-findings.md` before moving on.

### Step 3.5: Confirm repos and base branches

Only when more than one repo is involved, or the list is not obvious: list the repos and ask "Correct? (yes / add / remove)". With a single obvious repo, skip this and show repo and base branch together at Step 7, so the user approves once. Resolve each base branch from `git symbolic-ref --short refs/remotes/origin/HEAD` and show it; the user can override. Three services or fewer is the sweet spot. Four or more: say so and suggest splitting the ticket.

**Epic base branch.** Default is **none**: one PR per repo, straight to that repo's base. A repo that carries **two or more** PRs gets `<key-lowercase>-base`, and all of its PRs target it (one may stack on another with `base: pr:<id>`). The implement skill cuts it from the repo base and opens a final PR from it to the repo base; that PR is not in `prs` or `merge_order`, and `deploy_notes` says never to deploy with only part of the stack merged. Worked example in `references/plan-format.md`.

### Single-repo changes

When Step 3 finds that the change lands in one repo and no call, event, UI request or config key crosses a service boundary, take the short path:

- Skip Step 3.5's confirmation and the "three services or fewer" check. Show the repo and base branch at Step 7.
- Write the minimal `contract.md` from Step 4 (no contract items). Every boundary you read and found unchanged is named there with its file, because that evidence is how you know the change is single-repo.
- One PR, `implements: []`, `role: none`, `depends_on: []`. Two or more PRs in the repo still follow the epic base branch rule in Step 3.5.
- The test matrix has no compatibility cases, because no contract item exists.
- The critic pass (Step 6) still runs, with the contract axis limited to checking that nothing crosses a boundary.
- If you find a crossing later, leave the short path: write the contract items and carry on as a multi-repo plan.

### Step 4: Write the contract

One item per boundary crossing found in Step 3: REST endpoint, event, UI-to-API call, or config key. Each names producer, consumer, exact shape with a placeholder example, errors, compatibility, deploy order, the files on both sides, and the analog it copies.

A change contained in one service has none. Then `contract.md` carries `Repos:`, `Approved:`, a `## No contract items` section and a `## Boundaries checked and left unchanged` list (each with the file read), and every PR has `implements: []`, `role: none`. Shape in `references/plan-format.md`.

### Step 5: Write the plan and PR strategy

**You MUST read `references/plan-format.md` before writing `plan.md`, `contract.md` or `pr-strategy.yaml`. Do not improvise the yaml fields, types or nesting: the implement skill parses them.**

- One PR per repo unless a repo's change is genuinely two concerns.
- `depends_on: []` wherever the contract is enough. A non-empty `depends_on` needs a reason; the usual real one is a shared library the other repo must consume first.
- **Runtime data comes from a migration.** Data a code path needs at runtime (reason presets, flags, lookup rows read with raising finders) is created by a database migration, so it exists on deploy. Deploy notes saying "run this task first" are a smell: flag it to the user and prefer a migration, unless the repo convention or the user says otherwise.
- **Invariant writers.** When the plan introduces or relies on an invariant (a column kept equal to another, a single flagged row), list every other writer that bypasses callbacks (bulk updates, imports and mapping jobs, nested saves, maintenance scripts, data masking) as a required row under risks, each with a decision: enforce, accept or note.
- Every `status: active` requirement lands in at least one PR's `requirements`. An orphan is a plan bug: fix it before emitting.
- **Test matrix**: when using a spec, start from its Edge cases and Test seams sections, and keep each case's `Req #`. One row per case, per active requirement: positive, negative, edge, plus a **compatibility case** per contract item (the other side not deployed yet). Buckets: `unit` (written with the code, runs in CI; ids `UT-N`) or `manual` (staging check before merge). Each case has one owner PR. **Ids:** `TC-N` is reserved for `test-plan.md`. If `<workspace-root>/<key>/test-plan.md` exists, read it: `manual_checks` and the matrix's manual rows cite its `TC-N` ids and invent none. Only with no test-plan.md, write manual rows as `MC-N`.
- **Conflict check**: two PRs in one repo touching the same file or adding migrations: stack them (`base: pr:<id>`) or sequence them; record it under `conflict_risks`.
- **Lint before the critic.** After writing the plan files, run `python3 <path-to-spec-skill>/scripts/epic-lint.py <workspace-root>/<key-lowercase> --stage plan`. Fix its ERRORs; mention its WARNs in the Step 7 summary. If the script is not installed, print a one-line note and continue.

### Step 6: Critic pass

Spawn one top-tier-model agent over `plan.md`, `contract.md`, `requirements.yaml`, `pr-strategy.yaml` and `test-plan.md` when it exists (not the PRD or code). It returns `blocking` / `advisory` findings on three axes:

- **coverage**: every active requirement maps to a PR, a unit case and, with a test-plan.md, a test-plan case; also any behaviour decision that lives only in `plan.md` and not in the spec is `blocking`.
- **contract**: both sides of every item named, deploy order consistent with `merge_order`, no hidden code dependency.
- **blind spots**: breaking changes, migrations, auth, personal data, the other region/variant of a service.

Fix `blocking` before Step 7; carry `advisory` into the checkpoint. If the agent errors, warn and continue.

### Step 7: Decision point

Show the plan summary: services, contract items (one line each), PRs with `depends_on`, merge and deploy order, test matrix size, risks, open questions, and the workspace path. With a single repo that skipped Step 3.5, include the repo and base branch here. For a single-repo plan list "Contract items: none" and leave out merge and deploy order sections that have nothing to order. Ask: "Plan ready. implement / adjust / stop?"

An unqualified yes ("go", "looks good", "ship it") means implement. A yes with a change ("go, but drop the <service-b> PR") means adjust first. On approval set `Approved: yes` in `contract.md`. For a single-repo plan this one approval of the plan summary is the only stop: there is no separate contract review.

### Step 8: Hand off

Invoke `<implement-skill> <KEY>`. It owns everything from here: worktrees, parallel agents, tests, pushes, PRs and CI. `build` never duplicates those steps. In plan mode with a "stop", tell the user the next command is `<implement-skill> <KEY>`.

## Rules

- **Always include tests.** Every PR in the plan has unit cases (`UT-N`); every contract item has a compatibility case. No `TC-N` outside `test-plan.md`.
- **Follow existing patterns.** Each new endpoint, client method, event or screen names its analog.
- **Branches** `<type>/<KEY>/<short-kebab>` (`feat`, `fix`, `chore`). **PR titles** `<KEY> | <title>` (adapt to your convention).
- **Scope control.** More than 5 PRs or about 1000 lines: flag it and suggest splitting the ticket.
- **Auto-compact.** After heavy steps, write findings to `state/` first, then compact the context, then read them back. Never compact between Step 7 and Step 8: it can strip the yaml.

## Examples

**Service A + service B: remind the user when a <record> stalls.** Step 3 starts at service A's status-change code and follows the existing campaign trigger into A's client package for service B, then into B's `POST /api/v1/triggered/campaign`. C1: B accepts a new campaign code and renders it (producer B, consumer A). Two PRs, `depends_on: []`. Merge order B then A, because merging deploys and A must not trigger a campaign B does not know. A's compatibility case: B rejects the unknown code, and A reports it without retrying forever.

**Frontend + gateway + backend: new eligibility question.** The frontend calls the gateway, and the gateway calls the backend. Two contract items, three PRs in parallel, merge order backend, gateway, frontend.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A repo has no local checkout | Not cloned | Offer to clone it; never plan a side you cannot read |
| PRs keep needing `depends_on` | Contract too vague to code against | Tighten the item: exact names, types, status codes, example |
| API docs and controller disagree | Generated docs are stale | Trust the controller and its request test; note the drift as a risk |
| Bug plan built on a cause production never shows | Root cause read from code only | Step 3, item 5: aggregate the failing records before planning the fix |
| Tracker connector fails mid-run | Token expired | Reauthenticate; do not continue on a half-read ticket |
| Ticket links a shared doc, only an "authenticate" tool loads | Drive connector not signed in, or signed in after this session started | Connect it, restart; meanwhile the doc is an Open Question |
| Epic plan misses a child's requirement | Only the epic, or only open children, were read | Re-run Step 1.2: every child and subtask, every status, every comment |
