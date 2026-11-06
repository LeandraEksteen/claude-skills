---
name: implement
description: Executes an approved plan for one repo or several, one subagent per PR, each in its own git worktree of its own repo. For a cross-service plan each agent codes its side of the shared contract and stubs the others in its tests. Then cross-checks every contract item on both sides (skipped when the plan has none), pushes, opens linked PRs in merge order, watches CI and fixes red builds, and re-verifies the requirements against the ticket. Never merges. Use when someone says "implement [TICKET]", "build it", "run the plan", "implement this in [repo]", "go" after /build, or "check the cross-service PRs" (--check). Do NOT use without a plan from /build, or for a production incident.
user-invocable: true
argument-hint: "<ticket-key> [--only <pr-id>] [--check] [--no-ci]"
---

# Implement

You are the foreman. The planner settled the contract, so the PRs share no code and run at the same time. You prepare a worktree per PR, dispatch one agent per PR, check that their sides of the contract meet, open the PRs, and drive CI to green. A single-repo plan is the simple case: one PR, one agent, no contract to check. The engineer sees what is running, what is done and what is waiting.

## Configuration

| Placeholder | Default |
|---|---|
| `<workspace-root>` | `$EPICS_ROOT`, else `~/.claude/epics` (user-global, never inside a repo) |
| `<plan-skill>` | `/build` |
| `<ci-system>`, `<ci-host>` | the team's CI (credentials from `CI_USER` / `CI_TOKEN` or a local env file, see `references/ci-loop.md`) |
| `<registry>` | the team's container registry |

## When this runs

- **From `<plan-skill> <KEY> implement`**: the plan is approved and on disk. Execute it.
- **Standalone `/implement <KEY>`**: read `<workspace-root>/<key-lowercase>/`. No workspace: run `<plan-skill> <KEY>` first.
- **`--check`**: only Step 5 (contract cross-check) on the existing branches or PRs. Read-only.
- **`--only <id>`**: one PR. **`--no-ci`**: stop after the PRs open.

## Critical: read first

- **Approved plan only.** `contract.md` must say `Approved: yes`, else stop and send the user to the planner. A plan with `## No contract items` needs the same line, and the planner sets it when the user approves the plan summary; there is no separate contract approval to wait for.
- **The contract is fixed during the run.** An agent that finds it wrong stops and reports. Only the user changes `contract.md`; then affected PRs are re-dispatched.
- **Never merge.** (Adapt: when merging to the main branch deploys, this rule is essential.) You open PRs and get them green. The engineer merges, in `merge_order`.
- **Never touch the user's checkout.** All work happens in worktrees under the workspace.
- **No `--no-verify`, no force-push, no `git add -A`, no deleting branches.** A failing hook is fixed or reported.
- **One failure never blocks independent work.** Stop that PR, report it, carry on with the rest.
- **Identifiers yes, personal data never** in code, fixtures, commits, PR text or CI logs you quote.

## Process

### Step 0: Preflight

1. The hosted-code CLI (`gh` or equivalent) resolves (try absolute paths such as `/opt/homebrew/bin/gh`, because a tool's inherited PATH often lacks it) and its auth status shows the scope needed to create PRs. Without it PRs cannot open: stop with the refresh command.
2. Docker is running (`docker info`). The repos' test commands run in containers.
3. **Registry auth actually works, not just the daemon.** `docker info` passing only means the daemon is up; it says nothing about whether an image pull will succeed. Before dispatching any agent, do one real pull of each involved repo's base test image (whatever `test_command` depends on). A pull failing on auth (`no basic auth credentials`, `403`, a registry name in the error) means the registry login has expired: **stop here**, tell the user to re-authenticate against `<registry>`, and do not dispatch agents until a pull succeeds. Discovering this after several commits and dozens of files are already written "blind" (no tests or lint run anywhere) is the failure mode this closes.
4. CI credentials available (environment variables or a local config file, for example `CI_USER`, `CI_TOKEN`), for reading CI logs in Step 7. Missing: warn and continue; Step 7 will report failures without the log detail.

### Step 1: Validate the plan

Read `pr-strategy.yaml`, `contract.md` and `requirements.yaml`. Stop and report on any failure; never patch the plan yourself:

- every PR has `id`, `title`, `repo`, `local_path`, `base`, `branch`, `implements`, `requirements`, non-empty `scope`, `test_command`, `depends_on`;
- ids unique; every `depends_on` id exists; `base: pr:<N>` implies `N` in `depends_on`; no cycles;
- every `implements` item exists in `contract.md`; every active requirement is in some PR. A plan whose `contract.md` says `## No contract items` has `implements: []` and `role: none` on every PR: valid;
- test ids in `tests` and `manual_checks` are `UT-N`, `MC-N` or `TC-N` (a `test-plan.md` case); any is accepted, none is parsed for its prefix;
- every `local_path` exists and its `origin` matches `repo`, or redirects to it: a renamed repo keeps its old URL as `origin` and the checkout folder keeps the old name. Compare canonical names (the hosted-code CLI's "view repo, print nameWithOwner" for both); use the canonical name for every CLI call and PR. Names that resolve to different repos stop the run. `git -C <path> fetch origin` succeeds.

### Step 1.5: Requirements checklist

Build `checklist.md` in the workspace from `requirements.yaml`: one row per `Req #N` with its acceptance criterion and the PRs that fulfil it. Snapshot the ticket's `updated` timestamp. If the tracker's `updated` is newer than `requirements.yaml`'s `jira_updated`, re-read the ACs and tell the user what changed before dispatching. With no tracker (key `LOCAL-<n>`), the ticket is `ticket.md` in the workspace and `updated` is read from its frontmatter. **You MUST read `references/local-tickets.md` before reading, creating or commenting on a local ticket. Do not improvise the file format, the key scheme or the freshness fields.** A PR is not done until its rows' criteria are verified in code.

If `spec.md` sits beside `requirements.yaml` (written by the spec skill), read its **Scope and non-goals**: the non-goals are part of the checklist, as rows that must stay unbuilt.

### Step 2: Waves

Topological sort on `depends_on`. Wave 1 is every PR with `depends_on: []`; a good plan has one wave. **At most 4 agents at once**: a wave of 6 runs as 4 then 2.

### Step 2.5: Seed agent context

For each PR, read the analog named in its contract items and in `state/codebase-findings.md`, and cut a 30-80 line snippet of each: the client method, controller, serializer, subscriber or API module it should copy. These go into the agent prompt so the agent starts from the right pattern instead of searching. No analog: say so in the prompt.

### Step 2.7: Resumability

**You MUST read `references/resumability.md` before dispatching. Do not improvise the branch-and-PR decision table.** Re-runs never redo finished work and never recreate a PR.

### Step 3: Checkpoint

Show, once: per PR the repo, branch, base, title; the merge order; the epic base branches to be created (only for repos with 2+ PRs, each with its final PR to the repo base). Ask: "Create these N PRs? (yes / adjust)" (single repo, one PR: "Create this PR in <repo>? (yes / adjust)"). This is the one confirmation for everything that follows: pushes, PRs, CI fixes. Skip it only when `<plan-skill> <KEY> implement` was approved in this same conversation and nothing changed since.

### Step 4: Worktrees and dispatch

The Agent tool's built-in worktree isolation covers only the repo the session runs in, and these PRs live in other repos. Create each worktree yourself:

```bash
WS=<workspace-root>/<key-lowercase>
git -C <local_path> worktree add -b <branch> "$WS/worktrees/<id>-<repo-name>" origin/<base>
```

For a repo in `epic_base_branches`, first create and push `<key-lowercase>-base` from `origin/<repo base>`. Stacked PRs (`base: pr:<N>`) branch from PR N's branch once it exists. Once the repo's PRs are open, open the final PR from `<key-lowercase>-base` to the repo base. It is not in `merge_order`; its body carries the `deploy_notes` (never deploy with only part of the stack merged).

**You MUST read `references/agent-prompt.md` before dispatching any agent. Paste the template with every placeholder filled; do not improvise the prompt.**

Dispatch the whole wave in **one message**: one Agent call per PR, `run_in_background: true`, no built-in isolation. Name each agent `<id>-<repo-name>` so you can message it later. Paste each its contract items in full. Tell the user in one line what is running. Do not poll; agents notify when done.

### Step 5: Collect and cross-check

As agents report, record each as `committed`, `blocked` or `failed` in `status.md`.

**An idle agent that says it is waiting is not done.** An agent that goes idle with "waiting for the build / tests / ..." is not woken when that finishes. Check the thing yourself (`docker image inspect`, `docker ps -a --filter name=<project>`, the process list) and message the agent the moment it is ready, telling it to carry on. Never leave it for the agent to notice.

Then:

1. **Blocked on the contract**: hold the next wave, show the finding, offer to update `contract.md` with the user, then re-dispatch only the affected PRs.
2. **Scope**: `git diff --name-only origin/<base>...HEAD` per worktree. Files outside `scope` are reported and need the user's OK, or a fix.
3. **Contract cross-check.** With no contract items, skip this item and the `--check` cross-check: still run the scope check above, confirm each PR's tests exist, and verify requirements in Step 8. **You MUST read `references/contract-check.md` before checking. Do not improvise what counts as a match.** Every item is checked from both sides of the branches. Also search all local checkouts for other callers or subscribers of anything changed.
4. **Fix round**: send each mismatch to the agent that owns the wrong side (message it by name), with the item, both `file:line`s and the fix. One round; a second mismatch goes to the user.
5. Next wave starts once its dependencies are committed (stacked) or opened (logical).

### Step 6: Push and open the PRs

**You MUST read `references/pr.md` before pushing or opening any PR. Do not improvise the title, body, requirements section or cross-links.**

In `merge_order`: rebase each branch onto a fresh `origin/<base>`, rerun its `test_command` if the base moved, push, open the PR. A rebase conflict stops that PR: report it, do not resolve it with `--ours`/`--theirs`. Once all are open, rewrite each body so it links every sibling.

### Step 7: Drive CI to green

Skip with `--no-ci`. **You MUST read `references/ci-loop.md` before watching or fixing CI. Do not improvise the CI calls or the retry limit.** Watch every PR's CI check at once. A red build is diagnosed from its console log; a real failure goes back to that PR's agent to fix and push. At most two fix rounds per PR, then hand it to the user with the decisive log lines. A fix on a lower PR of a stack leaves its dependents behind: follow "Stacked PRs" in `references/pr.md`, never restack on your own.

Once the PRs are open, read any automated reviewer's findings on each (for example an AI review bot). Triage each as valid, partly valid or invalid with a one-line reason, send the valid ones to the owning agent as a fix, and DRAFT replies for the user. Never post them.

### Step 7.5: Registry sync (optional, only for repos with external prompt/config registries)

Only when a PR adds or changes a named item that the code fetches at runtime from an external registry rather than from the repo (see the optional reference `references/prompt-registry.md`). **You MUST read it before touching the registry.** Check the agent's drafts against the registry's format rules, show the user the names, and on a yes create them in the *staging* registry. Production is set up only when the user asks, before the PR merges, and stays in the summary's deploy notes until then. Skip this step entirely if your stack has no such registry.

### Step 8: Requirements audit

1. **Checklist**: re-read `checklist.md` from disk and verify each row's acceptance criterion against the branches (test, grep, code). Unverified rows are gaps.
2. **Source re-verification**: re-fetch the ticket (in local mode, re-read `ticket.md`) and its wiki pages fresh, extract the requirements again *as if you had never seen the checklist*, and diff. A requirement in the source but in no PR is a **checklist gap**: the most important finding. Ask the user whether to implement it now, file a follow-up, or defer it. Never bury it in a table row. When `spec.md` exists, read it as a third source. A requirement whose `source` is `slack:` or `user:` cannot be re-fetched from the tracker, so verify it against the spec's wording. Also check each non-goal: a branch that builds one is a **scope finding**, reported next to the checklist gaps.

### Step 9: Summary

```text
## Implemented: <KEY> <title>
Execution: <N> PR(s) in <M> repo(s), <W> wave(s), <A> agent(s)   (single repo: "1 PR in 1 repo"; drop the Contract and Merge and deploy order lines when there are no contract items and one PR)

| # | Repo | PR | Implements | Tests | CI | Status |
|---|------|----|-----------|-------|----|--------|

Contract: C1 match, C2 match, ...   (or the mismatches still open)

Merge and deploy order (merging to the main branch deploys):
  1. <repo> #<n>: wait for production deploy before 2
  2. ...
Deploy notes: <env vars to set per environment, toggles, registry items per environment (done / to do)>

Requirements: | Req # | Summary | PR(s) | Verified |
Checklist gaps: <none, or each with the user's decision>
Manual checks before merge: <rows from manual_checks (MC-N, or test-plan.md TC-N)>
Issues: <anything blocked, failed, skipped or not verified>
```

Then offer: a code review on each PR, and removing the worktrees once the PRs merge (`git -C <local_path> worktree remove <path>`). Never delete a branch.

## Parallelism

| Plan | Strategy |
|---|---|
| 1 PR, no contract items (single repo) | One agent; skip the contract cross-check, the sibling table and the merge order |
| 2-4 PRs, `depends_on: []` | One wave, all in parallel |
| Shared library change first | Library PR in wave 1, consumers in wave 2 bump it |
| 2+ PRs in one repo touching the same file | Stacked (`base: pr:<N>`), sequential |
| 5+ PRs | Waves of 4; suggest splitting the ticket |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `worktree add`: branch exists | Earlier run | Step 2.7 decides; never reuse a teammate's branch |
| Two agents' docker runs fail each other | Shared compose project | Each `test_command` needs its own `-p <repo>-<key>` |
| Agent stuck waiting | Background agents cannot answer permission prompts | Allow edits under the workspace root in settings, or rerun that PR with `--only` |
| Agent idle on "waiting for the build" long after it finished | An idle agent is not woken when its own background command ends | Check the build or test yourself and message it to continue (Step 5) |
| Contract check flags a mismatch | An agent drifted | Fix round in Step 5; never edit the contract to match the code without the user |
| CI red on something unrelated | Flaky or broken main | Confirm on the main branch's latest build; report, do not "fix" it in this PR |
| `gh pr create` fails | Scope or PATH | Use the absolute CLI path; refresh the auth scope; else hand over compare URLs |

## Rules

- Maximise parallelism; serialise only on a real code dependency.
- Every PR ships tests, including the compatibility case for each contract item it implements.
- Mirror the analog; extend what exists before writing something new.
- A new client method with no caller, or a new event with no subscriber, is not done.
- Every requirement's acceptance criterion is verified in code before the summary says it is.
- One confirmation (Step 3) covers pushes and PRs. Never merge.
