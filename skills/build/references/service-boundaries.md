# How `<team>`'s services talk

> Team-owned file. The sections below are a template: replace each with how your services actually connect. Keep the structure.

Loaded by Step 3. The patterns below describe how services connect. They are not a list of services: find the services from the code. Named files are examples to orient by. Re-read them; never cite one in a plan without opening it.

## Finding a repo's checkout

Match on the `origin` URL, not the folder name, because a repo is often cloned under a different folder name than its canonical name. Provide a snippet like:

```bash
for d in ~/code/*/ ~/src/*/; do
  url="$(git -C "$d" remote get-url origin 2>/dev/null || true)"
  case "$url" in *<org>/<repo>.git|*<org>/<repo>) echo "$d" ;; esac
done
```

No checkout: ask where it is or offer to clone it. Read the base from `origin/<base>` after `git fetch`, never from whatever branch the checkout happens to be on.

**Fetch fallback.** If `git fetch origin` fails over SSH (no key), fetch over HTTPS and say which repos could not be refreshed: `git -C <repo> fetch https://<git-host>/<org>/<repo>.git <base>:refs/remotes/origin/<base>`.

**Checkout hygiene.** A checkout may sit on an unrelated branch with uncommitted edits, so never read its working tree. Read with `git show origin/<base>:<path>` and `git grep <pattern> origin/<base>`. Implementation happens in a worktree off `origin/<base>`.

## Explore-agent prompt

Every Step 3.2 agent gets this, filled in:

````text
Repo: <repo> at <local_path>. Read-only: change nothing.
REQUIRED: read only from origin/<base> (`git show origin/<base>:<path>`, `git grep ... origin/<base>`),
never the working tree, which may be on another branch with uncommitted edits. If `git fetch origin`
fails, use the HTTPS fetch fallback and say so.
Requirements in scope: <Req #N one line each>
Questions: <exact numbered questions: where the behaviour lives, nearest analog, boundary code on
this side, migrations, test and lint commands>
Return: under <N> words; file:line for every claim; say "not found" rather than guessing.
````

## The four kinds of boundary (describe each as your team actually builds it)

1. **REST, caller to service.**
   - Where does the caller keep its client? (A package per service, or `lib/`, `services/`, `clients/`.) Tell the agent how to find one: search the caller for the service's base-URL setting.
   - Config shape: env var naming convention for base URL and token (for example `<SERVICE>_BASE_URL`, `<SERVICE>_TOKEN`), where they are declared (a yaml file, a sample env file, a keys manifest), and that a new variable must be set in every environment *before* the code that reads it deploys, so it is always a deploy note.
   - How the callee documents its API (generated OpenAPI/Swagger from request specs, DRF schema, hand-written docs) and the rule that a changed endpoint updates its spec and generated docs in the same PR.
   - Calls can go both ways (callbacks, webhooks); check both directions.
   - Regions and variants: a service may run more than one deployment; a contract change must hold for each.
2. **Events (message bus).**
   - Publish and subscribe idioms for your bus, the naming convention for event names, how a subscriber binds, where long-running consumers live, and which existing subscriber to copy.
   - Whether payloads are *callbacks* (model + id + URL, subscribers re-fetch over REST) or full records. For callbacks a new field needs no event change, only the REST item.
   - What happens when a consumer raises (dead-letter?) and what alert that produces. Search **every** local checkout for subscribers to an event you change, not only the repos in the plan.
3. **UI to API.** Which frontends call which API hosts (note when a frontend calls a gateway, not the backend that owns the data, so a feature needing backend data spans three repos); where API modules and response types live.
4. **Shared libraries.** Which gems/packages are shared code. A change there is a real `depends_on`: the library releases first and the consumers bump it.

## Each repo's own commands

Never assume. Read the repo's task runner (Taskfile/Makefile/package scripts): the tasks CI runs name the compose file and service. Provide a table of typical shapes for your stacks:

| Stack | Test | Lint |
|---|---|---|
| Rails | `docker-compose -p <unique> -f <compose file> run <service> bundle exec rspec <paths>` | `bundle exec rubocop <files>` |
| Django | `docker-compose -p <unique> -f <compose file> run <service> tox -e <env>` | the repo's lint env |
| React/Vite | `yarn vitest run <paths>` (plain `yarn test` may start watch mode and never exit) | `yarn lint`, `tsc --noEmit` |

Note any extra per-repo checks (package-boundary checks, custom lint cops, a testing-rules doc every spec must follow).

**Parallel runs:** several agents run docker at once, so each test command carries its own project name, `-p <repo>-<key-lowercase>`. Without it, two runs share containers and databases and fail each other.

## CI and deploy

State: which CI system builds every PR, what status check name it reports, how to find a PR's job URL, and (critically) **whether merging to the main branch deploys staging and/or production**. If it does, the merge order in the plan *is* the production deploy order, and the plan must say so.
