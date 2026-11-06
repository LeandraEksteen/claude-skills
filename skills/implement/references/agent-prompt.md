# Agent prompt

Loaded by Step 4. Every agent gets the template below with each `[...]` filled from `pr-strategy.yaml`, `contract.md`, `checklist.md` and the Step 2.5 snippets. Resolve every placeholder before dispatch: an agent that receives a literal `[scope]` has no scope. Append the stack block that matches the PR's `stack`, plus any repo-specific block.

## Template

````text
You are implementing one PR of a cross-service change. Other agents are building the other
services at the same time, against the same contract. You cannot see their code and must not
need it.

## Your PR
Ticket: [KEY] - [ticket title]
PR: [id] "[title]" in [repo]
Worktree (work ONLY here): [worktree path]
Branch (already checked out): [branch], based on origin/[base]

## Contract items you implement (fixed)
[each item in `implements`, pasted in full from contract.md; none -> "No contract items: nothing crosses a boundary"]
Your role: [producer|consumer] of [C-ids] (role none: no contract items)

If an item is wrong, ambiguous, or cannot be built as written, STOP. Commit nothing for it and
report: the item, what you found, the file:line that shows it, and the smallest contract change
that would fix it. Never build your own variant.

## Requirements this PR fulfils
[checklist rows for this PR: Req #N, summary, acceptance criterion]
Before you report done, check each criterion holds in your code: grep it, read it, run it.

## Scope (authoritative)
You may create or edit only: [scope list]
If the change needs a file outside it, stop and report which and why.

## Changes
[changes]

## Patterns to follow
[Step 2.5 snippets, each with its source path. Or: "No analog found for <thing>: search the repo
for the nearest similar code before writing new code of that kind."]
New code structurally matches these: same base classes, client helpers, serializer style, test
layout. Deviate only with a reason you put in your report.

## Tests to write
[tests list from the PR's yaml entry, one per line, ids kept (UT-, MC- or TC-)]
Stub the other services: [stubs]
Cover the contract example AND the compatibility case: the other side not deployed yet, the field
missing, the event absent, the endpoint rejecting the call. Never call a real or shared
environment, and never call another agent's branch.

## Process
1. Read the repo's own instructions if present: CLAUDE.md, AGENTS.md, contributor and copilot
   instructions, docs on testing.
2. Read every file before changing it, and read each analog end to end.
3. Write the code, then the tests. Tests are not optional.
4. Integration is part of done. A new client method must have a caller; a new event a publisher
   and the subscriber the contract names; a new API module a component that uses it. Grep for it.
5. Run: [test_command]
   Run every build and test command in the foreground, with the Bash timeout raised to 600000 ms.
   If one can take longer (a first `docker-compose build`), start it in the background and wait for
   it inside the same turn with a loop that checks for the result (e.g. `until docker image inspect
   <image> >/dev/null 2>&1; do sleep 30; done`). Never end your turn while waiting on your own
   command: an idle agent is not woken when its background command finishes, only by a message.
   Fix what you broke. A failure that is not yours must also fail on origin/[base]: commit your
   work, `git checkout --detach origin/[base]`, run that test, `git checkout [branch]`. Report it;
   do not fix it.
   If Docker or the tests cannot run, the static pre-push checklist is mandatory; report each check
   as done:
   - (a) Every method called on another object or class is public: find the visibility modifier in
     the callee before calling.
   - (b) Every raising lookup (find-or-fail style) of a seeded row has that row created in the test
     setup, and the production seed exists via a migration.
   - (c) Feature flags and integrations are switched on only after the records whose callbacks would
     fire exist (lazy-fixture ordering).
   - (d) Nested-attributes saves are checked against reject rules: a row with only an id and a flag
     may be dropped.
   - (e) Factories/fixtures that trigger sync callbacks are built so the callback has its parent
     record.
6. Run the simplify/cleanup pass on your changes, then the tests again.
7. Lint changed files only: [lint_command]. Never reformat untouched code.
8. Self-review the diff for security: secrets in code, SQL built from input, unauthenticated new
   endpoints, personal data in logs or error messages. Fix what you introduced; report anything
   pre-existing, do not fix it unasked.
9. Commit specific paths only (never `git add -A` or `git add .`). Message: `[KEY] | <summary>`.
   Never --no-verify; a failing hook is fixed or reported.
10. Do NOT push and do NOT open a PR: the orchestrator does that after checking every service's
    side of the contract. Do not touch any other repo, or the user's checkout at [local_path].

## Never
- Real customer data in code, fixtures, specs, logs or commits. Placeholder IDs only.
- Secrets in code. New config comes from env through the repo's config files.
- Changing the contract to fit the code.

## Report back with exactly these headings
Status: committed | blocked | failed
Commits: <sha> <subject>, one per line
Files changed: one per line
Contract items: per C-id, the file:line that implements it on your side
Requirements: per Req #N, how its acceptance criterion was verified
Tests: command, passed/failed counts, new test files, which test is the compatibility case
(tests could not run -> the static pre-push checklist, a-e, each marked done)
Out of scope / follow-ups: what you noticed and left alone
Blocked or failed: the reason, with the decisive error line

You may get follow-up messages (a contract mismatch, a CI failure). Fix them in the same worktree,
rerun the relevant tests, commit, and report back the same way.
````

## Stack blocks (append the matching one; the team should maintain its own)

**rails**

````text
## Rails
- Run the repo's package/module-boundary check (if it has one) for changed packages; a new
  cross-package reference needs a declared dependency, not a violation.
- Outbound HTTP is stubbed (WebMock or equivalent), the body taken from the contract example.
- A changed endpoint updates its API-doc spec and regenerates the docs inside the test container;
  commit the generated file with the code.
- Migrations are additive: new columns nullable or defaulted. No rename or drop in this PR.
- Honour any custom lint rule the repo enforces in CI (for example, bulk-write helpers on tables
  that feed a delta/incremental load must also set `updated_at`). Grep your diff for the
  offending calls, and run the linter on changed files when you can.
- Event bus: publish the exact event name in the contract. A new subscriber is wired where the
  repo wires its others; copy the analog.
- When done: `docker-compose -p <same project> -f <same compose file> down -v`.
````

**django**

````text
## Django
- Tests run through tox in the repo's test container, with the unique -p project name.
- Outbound HTTP is mocked in the style of the nearest existing test.
- A changed endpoint keeps its serializer and generated API schema correct.
- Migrations are additive: new fields null=True or with a default.
````

**react**

````text
## React
- Install with the lockfile frozen (`yarn install --frozen-lockfile`). Do not change the lockfile
  unless a new dependency is needed, and then say so.
- API calls go through the repo's API module for that domain; types for new shapes sit beside it,
  written from the contract's Shape.
- Tests: `yarn vitest run <paths>` (plain `yarn test` may watch forever), the repo's lint and
  type-check scripts. Mock the API module or axios, never the network.
- The old response shape (field absent) renders without errors; a test shows it.
````

**Optional extra block (repo with an external prompt registry)**: append only to PRs in such a repo, whatever its `stack`. Content: "Prompts and schemas live in the registry, not in the repo. For every new or changed registry name, write the full text to `<workspace-root>/[key-lowercase]/state/registry-drafts.md`, one section per registry name, the body in a fenced block. Follow the registry's format rules (see `references/prompt-registry.md`). Tests run with the repo's own command; if dependencies cannot install, run what you can and say which tests did not run."
