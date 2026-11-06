# Plan format

Loaded by Steps 1 and 5. The implement skill parses `contract.md`, `requirements.yaml` and `pr-strategy.yaml`, so these shapes must stay exact. All files go in `<workspace-root>/<key-lowercase>/`.

## requirements.yaml

```yaml
schema_version: 1
key: TICKET-1234
jira_updated: 2026-10-02T09:14:00Z    # the ticket's `updated` when extracted
jira_content_sha: <sha256 hex>        # optional: sha256 of summary + "\n" + description, set by the spec skill
requirements:
  - id: 1                              # Req #1. Append-only: never renumber, never delete
    summary: Service A triggers the stalled-<record> campaign after 7 days without progress
    category: functional               # functional | edge-case | business-rule | data-contract | operational | out-of-scope
    source: jira-ac                    # jira-ac | prd:<page title> §<section> | child:<KEY>
    source_text: "<verbatim text it came from>"
    acceptance: <checkable: a spec that asserts X, a grep that finds Y, a staging check that shows Z>
    status: active                     # active | blocked | out-of-scope | dropped
    blocked_on: null                   # when blocked: "<question> - <who decides>"
```

A file written by the spec skill has `origin: to-agent-spec` at the top and may carry extra optional fields per requirement: `decided_by`, `supersedes`, `domain` and `risk`. Keep them when you copy or append requirements. `source` may also be `jira-comment`, `slack:<permalink>` or `user:<date>`. `key` and `jira_updated` are null until the ticket exists, and the implement skill needs both set. `jira_content_sha` is optional; Step 1.0 uses it to tell an edited ticket from a merely touched one.

On a re-run, load the existing file, keep ids for matching requirements, append new ones, and mark vanished ones `dropped`. PR bodies cite `Req #N`, so an id never changes meaning.

## contract.md

One section per boundary crossing. Every field is required; write `none` rather than leaving one out.

````markdown
# TICKET-1234 contract

Repos: service-a, service-b
Approved: no            # build Step 7 sets yes; the implement skill refuses no

## C1: service-b accepts the stalled_record campaign code

- Kind: rest            # rest | event | ui-api | config
- Producer: service-b
- Consumer: service-a
- Interface: POST api/v1/triggered/campaign   (event: full event name; config: the variable)
- Change: new accepted value `stalled_record` for `campaign_code`
- Shape:
  ```json
  { "campaign_code": "stalled_record",
    "customer_id": "00000000-0000-0000-0000-000000000000" }
  ```
- Errors: unknown campaign_code -> 4xx with an error body (status as the controller returns today)
- Compatibility: additive. Old service A never sends the new code.
- Deploy order: producer first. Service A deploying first gets the 4xx and must not retry forever.
- Producer files: config/routes.rb, app/controllers/api/v1/triggered/campaign_controller.rb, spec/...
- Consumer files: <path of the client in service A>, <path of the code list>
- Analog: <the existing endpoint, event or campaign this copies, with path>
````

### No contract items

A change contained in one service has no boundary to settle. This is the single-repo case: one PR, no compatibility cases, and this short `contract.md` is the only contract work. Write it like this, never an empty file:

````markdown
# TICKET-1234 contract

Repos: service-a
Approved: no

## No contract items

All behaviour is inside service-a; nothing crosses a service boundary.

## Boundaries checked and left unchanged

- service-b campaign client: <path> (read on origin/main), unchanged
- event `records.updates`: <publish site path>, payload unchanged
````

Each unchanged boundary names the file read. In `pr-strategy.yaml` every PR has `implements: []` and `role: none`. The implement skill skips the contract cross-check for such a plan and still verifies scope, tests and requirements.

Rules:

- **Shape is exact**: names, types, nullability, enum values, a placeholder example. No real data.
- **Events** also state the exchange or topic the subscriber binds, the payload class, and whether subscribers re-fetch or read the payload.
- **Compatibility** is `additive` or `breaking`. `breaking` names its expand / migrate / remove releases and cannot ship as one PR pair.
- **Files** are real paths read on the current base; new ones marked `(new)`.

## pr-strategy.yaml

```yaml
schema_version: 1
key: TICKET-1234
title: Remind users when a <record> stalls
jira: https://<tracker-host>/browse/TICKET-1234
epic_base_branches: {}        # repo -> "<key-lowercase>-base", only for repos with 2+ PRs (see Epic base branches)
prs:
  - id: 1                                   # integer, unique, by order of appearance
    title: "TICKET-1234 | Accept stalled_record campaign"
    repo: <org>/service-b
    local_path: /path/to/checkouts/service-b
    base: main                              # repo base, its epic base branch, or "pr:<id>" to stack
    branch: feat/TICKET-1234/stalled-record-campaign
    stack: rails                            # rails | django | react | other  (extend for your stacks)
    implements: [C1]
    role: producer                          # per item if mixed: {C1: producer, C2: consumer}
    requirements: [1]
    scope:                                  # the only paths this PR may touch; dirs end in /
      - app/controllers/api/v1/triggered/
      - app/services/campaigns/
      - spec/
      - swagger/
    changes: |
      Register the campaign code, render its message, request spec, regenerate API docs.
    stubs: none                             # how tests fake the other side
    tests:                                  # this PR's test-matrix cases
      - UT-1 [positive] accepts stalled_record and enqueues the message
      - UT-2 [negative] unknown code still rejected
    test_command: >-
      docker-compose -p service-b-ticket-1234 -f docker-compose.yml
      run -e RAILS_ENV=test service-b-test bundle exec rspec spec/requests/triggered
    lint_command: bundle exec rubocop
    depends_on: []
    depends_reason: ""
  - id: 2
    title: "TICKET-1234 | Trigger stalled-record campaign"
    repo: <org>/service-a
    local_path: /path/to/checkouts/service-a
    base: main
    branch: feat/TICKET-1234/stalled-record-campaign
    stack: rails
    implements: [C1]
    role: consumer
    requirements: [1]
    scope:
      - <client package path>/
      - app/jobs/
      - spec/jobs/
    changes: |
      Add the campaign code, trigger it from the stalled-record job.
    stubs: HTTP stub of POST api/v1/triggered/campaign: success, and the 4xx for an unknown code
    tests:
      - UT-3 [positive] stalled record triggers the campaign once
      - UT-4 [compatibility] service B rejects the code -> reported, no retry loop
    test_command: >-
      docker-compose -p service-a-ticket-1234 -f docker-compose.test.yml
      run -e RAILS_ENV=test service-a bundle exec rspec <client package>/spec spec/jobs
    lint_command: bundle exec rubocop
    depends_on: []
    depends_reason: ""
merge_order: [1, 2]                         # merging deploys: producers before consumers
deploy_notes: service B must be live in production before the service A PR merges.
manual_checks:                              # rows no spec can assert; cite test-plan.md's TC-N when it exists
  - MC-1 [manual] staging: the stalled-record message renders correctly
conflict_risks: []                          # same-repo file overlaps / migration collisions, with mitigation
```

Rules:

- **Test ids have three namespaces.** `UT-N` unit cases (the `tests` lists). `MC-N` manual rows the planner writes itself, only when no `test-plan.md` exists. `TC-N` is reserved for `test-plan.md` cases. When `<workspace-root>/<key>/test-plan.md` exists, `manual_checks` and the matrix's manual rows cite its `TC-N` ids and invent none; never reuse a TC number for a unit or build-only case.
- `id` integers are positional; `branch` is the durable identity the implement skill resumes on.
- `base: pr:<id>` stacks on another PR's branch, and that id must also be in `depends_on`.
- `scope` is authoritative. Agents may not edit outside it, and the implement skill flags any file a branch changed outside it.
- `stubs` cover the contract example **and** the compatibility case.
- `test_command` runs only this PR's specs, with a unique `-p` compose project name. CI runs the full suite.
- A PR in a plan with no contract items has `implements: []` and `role: none`.
- Every active requirement appears in at least one PR's `requirements`. Every requirement has at least one test case.

## Epic base branches

A repo with one PR has no epic base branch: the PR targets the repo base. A repo with **two or more** PRs gets `<key-lowercase>-base`, and every one of its PRs targets it. A PR may stack on another with `base: pr:<id>` (that id must be in `depends_on`). The implement skill cuts the epic base from the repo base and, once the repo's PRs are open, opens the **final PR** from the epic base to the repo base. The final PR is not in `prs` or `merge_order`. `deploy_notes` must say never to deploy with only part of the stack merged.

```yaml
epic_base_branches: {service-a: ticket-1234-base}
prs:
  - {id: 1, repo: <org>/service-a, base: ticket-1234-base, depends_on: []}
  - {id: 2, repo: <org>/service-a, base: "pr:1",           depends_on: [1]}   # stacked on PR 1
  - {id: 3, repo: <org>/service-b, base: main,             depends_on: []}
merge_order: [3, 1, 2]
deploy_notes: Service A PRs 1-2 merge into ticket-1234-base; the final ticket-1234-base -> main PR deploys. Never deploy with only part of the stack merged.
```

## plan.md

In this order:

1. **Why this matters**: ticket, customer value, business impact.
2. **Architecture overview**: 2-3 sentences, and the call path across services.
3. **Requirements**: `Req #N` one line each, blocked ones with their question.
4. **Changes required**: one table per repo (file, change, complexity), plus migrations and their risk.
5. **Contract summary**: one line per item, with deploy order.
6. **PR strategy**: the yaml, as written to `pr-strategy.yaml`.
7. **Test matrix**: `| ID | Req | Case | Type | Bucket | PR |`, ID being `UT-N`, `MC-N` or the `test-plan.md` `TC-N`.
8. **Risks and mitigations**, **open questions**, **out of scope**, **estimated scope**.
