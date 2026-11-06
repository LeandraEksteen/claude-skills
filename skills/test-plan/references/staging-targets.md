# Staging targets

Loaded by Step 3 before telling anyone what to deploy. Repos get work onto staging in different ways, and
this file is the team's record of which. It starts empty and grows from the user's answers: never fill an
entry from a guess.

## The two ways

- **PR branch.** The PR's own branch is deployed to staging by hand once its CI is green. The commit under
  test is the PR's head commit.
- **Shared staging branch.** The repo deploys staging from a shared feature branch that several PRs are
  merged into. The PR's commit must be inside that branch, and the branch's own CI must be green, before
  anyone tests. The branch carries other people's work too, so testers may see unrelated changes.

## Per repo

| Repo | Staging comes from | Branch | Notes |
|---|---|---|---|
| _none recorded yet_ | | | |

## What to do for each repo in the run

1. Look the repo up above. Not listed: ask "Does <repo> deploy to staging from the PR branch, or from a
   shared branch? Which one?" Offer to add the answer to the table; add it only on a yes.
2. **PR branch:** `gh pr checks <number> --repo <repo>` must be green. The commit under test is
   `gh pr view <number> --repo <repo> --json headRefOid`.
3. **Shared branch:** the PR must be merged into the shared branch first. Check with
   `gh api repos/<repo>/compare/<shared-branch>...<head-sha> --jq .status`: `identical` or `behind` means the
   commit is already in the branch; `ahead` or `diverged` means it is not. Not in it: tell the user to merge
   it in, and stop for that repo. Then check the shared branch's CI is green
   (`gh api repos/<repo>/commits/<shared-branch>/check-runs --jq '.check_runs[] | [.name,.conclusion] | @tsv'`).
   Record the shared branch's tip commit as the commit under test.
4. Tell the user the order to deploy across repos: the plan's `merge_order`, a producer before its consumer.
5. Never deploy anything yourself.
