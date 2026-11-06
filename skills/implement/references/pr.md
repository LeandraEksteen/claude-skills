# Pushing and opening PRs

Loaded by Step 6. The user confirmed the PR set at Step 3; this is the mechanics.

## gh

The hosted-code CLI is often missing from the PATH a tool inherits. Call it by absolute path (for example `/opt/homebrew/bin/gh`, else `/usr/local/bin/gh`). It needs the scope that allows creating PRs.

## Rebase, push, open, in merge order

For each PR in `merge_order`:

```bash
W="$WS/worktrees/<id>-<repo-name>"
git -C "$W" fetch origin <base>
git -C "$W" rebase origin/<base>          # conflict -> git rebase --abort, stop this PR, report
git -C "$W" push -u origin <branch>       # never --force
gh pr create --repo <repo> --base <base> --head <branch> \
  --title "<KEY> | <title>" --body-file "$WS/pr-<id>.md"
```

If the rebase moved the base, rerun the PR's `test_command` before pushing. A rejected push means the remote branch changed: stop and report, never force.

If PR creation fails, hand over the compare URL and never report a PR that does not exist: `https://<git-host>/<repo>/compare/<base>...<branch>?expand=1`.

Open as **ready**, unless the user asked for drafts or the PR's local tests failed. Those open as drafts, and the body says which test failed.

## Body

Fill in the repo's own PR template first (for example `.github/PULL_REQUEST_TEMPLATE.md`, read from the worktree). Answer each of its headings. Then append the sections below, in this order: Requirements, Cross-service change, Test plan, Why this is split. "Cross-service change" only when the plan has two or more PRs; "Why this is split" only for a split. A single-repo plan with one PR gets the repo's template, the Requirements section and the Test plan, and nothing else.

### Requirements section

Mandatory. It is the durable record of what this PR fulfils, readable in a fresh session.

```markdown
## Requirements

- [x] Req #1: [TICKET-1234](<ticket url>)
      **Accept when:** a stalled record triggers the campaign exactly once (test: spec/jobs/...)
- [ ] Req #3: [TICKET-1234](...)
      **Accept when:** TBD - clarify with <reporter>
```

Local ticket (no tracker): write `[LOCAL-1234] (local ticket)` with no link, and give each row's `Accept when:` line in full, since a reviewer cannot open the ticket file. Do the same for the "Part of" line below.

Tick a row only when Step 8 verified it. Do not paste requirement text: the ticket is the source, and a copy drifts when the PRD changes. Vague criterion: `TBD`, visibly.

### Cross-service change

Only when the plan has two or more PRs. A single PR in a single repo skips this section and goes straight to the Test plan below.

```markdown
## Cross-service change

Part of [TICKET-1234](<ticket url>): <n> PRs built against one contract.

| # | Repo | PR | Implements | Merge order |
|---|------|----|-----------|-------------|
| 1 | service-b | <url> | C1 (producer) | 1 |
| 2 | service-a | <url> | C1 (consumer) | 2 |

No contract items but several PRs: write `none` under Implements and drop the Contract items list.

**Merging deploys.** Merge in the order above, and let each production deploy finish before the next.
<deploy_notes from pr-strategy.yaml>

**Contract items in this PR**
- C1: <one line>. Compatibility: <additive / what happens if the other side is live first>.
```

Do not paste the whole contract into the body: the one-line summary and compatibility note are what a reviewer needs.

### Test plan

Every PR carries it, including a single-repo PR. Drop `[compatibility]` rows when the PR has no contract items.

```markdown
## Test plan

- [x] UT-3 [positive] ... (test path)
- [x] UT-4 [compatibility] ... (test path)
- [ ] MC-1 [manual] staging: ... (before merge; or the test-plan.md TC-N)
```

### Why this is split

Every PR body of a split carries it, the final PR's too.

```markdown
## Why this is split

- **Dependency:** <depends_reason from pr-strategy.yaml; "none: independent via the contract">
- **Cost:** <rebases, stacked diff>
- **Deploy rule:** <merge order and what must be live first, from deploy_notes>
```

## Stacked PRs

When a fix lands on a lower PR of a stack, its dependents are behind it. Force-push is forbidden, so do not improvise: ask the user to choose between merging the base branch into the dependent, or a user-approved force-push of that one branch. Then re-check CI on the dependents. If the user already restacked it, verify with `git merge-base --is-ancestor <base-tip> <dependent>` and leave it alone.

## Link the siblings

The first PR opens before the others have URLs. Once all are open, rewrite every body with the full table: `gh pr edit <number> --repo <repo> --body-file "$WS/pr-<id>.md"`.

## Labels and reviewers

None unless the user asks. Code-owner rules assign reviewers, and automated reviewers run on their own.
