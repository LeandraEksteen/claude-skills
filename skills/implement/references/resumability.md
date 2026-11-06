# Resumability

Loaded by Step 2.7. State lives on the hosted-code platform and in the worktrees, so a killed `implement` is simply run again. For each PR, before creating its worktree:

```bash
GH=gh
WT="$WS/worktrees/<id>-<repo-name>"
BRANCH_ON_ORIGIN=no
git -C <local_path> ls-remote --exit-code --heads origin <branch> >/dev/null 2>&1 && BRANCH_ON_ORIGIN=yes
PR="$($GH pr list --repo <repo> --head <branch> --state all --json number,url,state --jq '.[0]')"
LOCAL=no; [ -d "$WT" ] && LOCAL=yes
```

| Worktree | Branch on origin | PR | Action |
|---|---|---|---|
| any | any | open or merged | Done. Record the PR, skip dispatch. Still use its branch for stacked children |
| any | any | closed, not merged | Ask: re-dispatch on a new branch name, or skip |
| yes | no | none | Agent finished or died before push. Check `git -C "$WT" log origin/<base>..`: commits -> go to Step 5 for this PR; none -> re-dispatch into the same worktree |
| yes | yes | none | Pushed but no PR: go straight to Step 6 for this PR |
| no | yes | none | Pushed from elsewhere. Ask: open the PR from it, or rename and rebuild |
| no | no | none | Fresh: create the worktree and dispatch |

`status.md` in the workspace is a convenience log, never the source of truth: the hosted-code platform and the worktrees win when they disagree.
