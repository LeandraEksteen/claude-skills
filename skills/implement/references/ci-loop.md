# CI loop

Loaded by Step 7. `<ci-system>` builds every PR and reports a status check on the hosted-code platform. It runs the repo's full suite and linters, so it catches what the agent's scoped `test_command` did not.

## Watch

Watch all PRs at once with one background command per PR, not a polling loop:

```bash
gh pr checks <number> --repo <repo> --watch --interval 60
```

Exit 0 is green. Non-zero is red or errored: read the failing check's URL from `gh pr checks <number> --repo <repo> --json name,state,link`.

**Watchers go stale on every push.** After each push, stop the old watcher and start a new one, and match the build number in the check URL against the new head sha before trusting a result.

## Read the failure

The check links to the CI job's build page. Pull the console log with the CI token, **with the login on stdin and never in argv**:

```bash
CI="https://<ci-host>"
E="$HOME/.config/<team>/.env"
envget() { sed -n "s/^$1='\(.*\)'$/\1/p" "$E" 2>/dev/null | tail -1; }
U="${CI_USER:-$(envget CI_USER)}"
T="${CI_TOKEN:-$(envget CI_TOKEN)}"
ci() { printf 'user = "%s:%s"\n' "$U" "$T" | curl -s -K - "$@"; }
ci "$CI/<job path>/PR-<n>/<build>/consoleText" > "$WS/ci-<id>-<build>.log"
```

(Adapt the URL scheme and credentials to your CI. The pattern that matters: credentials never appear on the command line or in output; the log goes to a file.)

The log is large: grep it for the framework's failure summary markers (for example `Failures:`, `rspec ./`, `Offenses:`, `Error`, `exit code`), never print it whole. Search for the failure summary first; the rest is noise. No token: report the check link, ask the user for the downloaded log, and do not guess a cause (never blame a stacked base branch without evidence).

A generic status text such as "This commit cannot be built" is **not** an infra signal. It can show when the test stage fails (many failed tests can sit behind one). Treat it as a red build and get the log.

## Classify

| Failure | Action |
|---|---|
| A test or lint offence in files this PR changed | Send to the PR's agent |
| A test this PR did not touch, that also fails on the main branch's latest build | Not this PR: report it, do not fix it here |
| A test this PR did not touch, green on main | This PR broke it: send to the agent, with the test and why it may be related |
| Infrastructure (image pull, timeout, agent offline) | Re-run once with an empty commit only if the user agrees; otherwise report |

Check main the same way: query the CI's JSON API for the main branch's last completed build.

## Fix

Message the PR's agent with: the failing test or offence, the decisive log lines, and "fix in your worktree, rerun the failing test, commit". When it reports back, you push the worktree's branch (never force). The push triggers a new build; watch again.

**At most two fix rounds per PR.** Still red: stop and hand the user the PR, the failing test and the decisive lines. Never skip, delete or disable a failing test to get green, and never weaken an assertion without saying so in the PR body.

## Reviews

An automated reviewer may comment on these repos on its own. When CI is green, offer to run a code-review skill on each PR; post with a "comment" flag only if the user asks.
