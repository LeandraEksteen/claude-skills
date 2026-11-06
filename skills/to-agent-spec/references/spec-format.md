# Spec format

Loaded by **Step 2** and **Step 4**. The planner reads `requirements.yaml` and the test-planner reads `spec.md`, so keep these shapes exact. Both files go in `<workspace-root>/<name>/`, the folder the planner already uses. `<name>` is the lowercase ticket key, or a confirmed slug while the work has no ticket; Step 5 renames it to the key once a ticket exists.

## The ledger (working notes, kept in `state/ledger.md`)

One row per statement found in a source:

| # | Statement | Source | Author | Date | Gap type |
|---|---|---|---|---|---|

`Source` is one of: `conversation:<date>` (this session's discussion), `file:<path>`, `ticket:<KEY> description`, `ticket:<KEY> ac`, `ticket:<KEY> comment`, `prd:<page title> §<section>`, `chat:<permalink>`, `gdoc:<title>`, `artifact:<title>` (hosted-workspace doc), `meeting:<title, date>`, `user:<date>` (an answer from the grill). `Gap type` is blank, or one of `conflict`, `silence`, `unanswered`, `stale`, `vague`. Keep the ledger in `state/` so it survives context compaction. The final spec cites sources; it does not reproduce the ledger.

(Important: the lint script's accepted `source` prefixes are fixed in code. If you rename prefixes, change `SOURCE_RE` in `scripts/epic-lint.py` to match.)

### Gap types and the question each becomes

| Type | Looks like | Question to ask |
|---|---|---|
| conflict | PRD says 7 days, a later comment says 5 | Which one stands? Recommend the later and more specific source unless it was an aside |
| silence | The ticket defines the trigger but not what happens on failure, to in-flight records, or who is notified | What should happen? Recommend the nearest existing behaviour, cited |
| unanswered | A comment asks "do we also cover <case>?" and nobody replied | Answer it, or move it to out of scope |
| stale | A decision a later comment reversed, or a Done child already built it | Confirm it is dead, or revive it |
| vague | "Should be fast", "handle edge cases" | What number or observable result makes it done? |

Silences worth hunting in any workflow-style product (adapt the list to your domain): failure and retry behaviour, in-flight and historic records, who is notified and through which channel, amounts and rounding, time zones, permissions, audit trail, what a re-run does. Also hunt for: what a hand-off such as "manual review" or "escalate" means for the people and systems who receive it, who owns an external system the work depends on, how work already part-way through the funnel is treated at launch, and which date counts when a record has two (fetched versus uploaded, created versus completed).

## requirements.yaml

The planner's schema (the planner's plan-format reference is authoritative), plus the fields marked new. The planner appends to this file on a re-run and never renumbers. `source` may be a quoted string of several sources, each starting with one of the prefixes. The lint script checks these shapes.

Optional `superseded_terms:` (a list of strings) names wording a later decision replaced. A `Superseded: "old term"` line in `spec.md` (for example in the decision log) does the same. The lint script then WARNs, with file and line, for every epic file (`spec.md`, `plan.md`, `pr-N.md`, `pr-strategy.yaml`, `checklist.md`) that still contains one. Marker lines themselves are not flagged. Run it after `--amend` to find what to refresh. Warnings only; the exit code is unchanged.

```yaml
schema_version: 1
key: TICKET-1234                      # null until a ticket exists; Step 5 fills it in
origin: to-agent-spec                 # new: the planner skips its own extraction for a file with this
jira_updated: 2026-10-02T09:14:00Z    # the ticket's `updated` when read; null with no ticket
jira_content_sha: 9f2c...             # optional: sha256 hex of summary + "\n" + description; the planner compares this, not jira_updated
requirements:
  - id: 1                             # Req #1. Append-only: never renumber, never delete
    summary: A stalled <record> triggers the reminder campaign after 5 days without progress
    category: functional              # functional | edge-case | business-rule | data-contract | operational | out-of-scope
    source: jira-comment              # jira-ac | jira-comment | prd:<page title> §<section> | child:<KEY> | slack:<permalink> | gdoc:<title> | artifact:<title> | meeting:<title, date> | user:<date>
    source_text: "<verbatim text it came from>"
    acceptance: <checkable: a spec that asserts X, a query that returns Y, a staging check that shows Z>
    status: active                    # active | blocked | out-of-scope | dropped
    blocked_on: null                  # when blocked: "<question> - <who decides>"
    decided_by: "jane.doe, 2026-10-03" # new: whoever settled it (author of the source, or the user)
    supersedes: "PRD §3 said 7 days"  # new: the conflicting statement this one overrode, else null
    domain: <domain-area>             # new: free-text or team-defined enum (e.g. checkout | identity | billing | notifications | other)
    risk: [state-transition]          # new, optional: e.g. money | pii | state-transition | external-integration | permissions
```

`domain` and `risk` let the test-planner pick its edge-case checklists. A dropped requirement keeps its id and gets `status: dropped` with the reason in `blocked_on`.

## spec.md

In this order. Short sentences. Everything checkable.

````markdown
# TICKET-1234: <title>        (no ticket yet: use the slug in place of the key)

Approved: no            # set to yes only after the user approves in Step 5
Sources read: <ticket keys, wiki pages, chat threads, each with date read>
Not read: <anything unreadable, with why>   # or "none"

## Goal and why
Who is affected (end user, operator, ...), what changes for them, and the business reason. Two to five sentences.

## Scope and non-goals
- In scope: one line each.
- Not in scope: one line each, each with who decided and when.

## Decisions
One row per requirement, in id order.

| Req | Decision | Acceptance | Decided by | Source |
|---|---|---|---|---|

## Conflicts resolved
| What differed | Source A | Source B | Winner and why |
|---|---|---|---|

## Edge cases and failure behaviour
Requirements of category `edge-case`, each with its acceptance. Include the silences the user filled.

## Test seams
The highest points where the behaviour can be checked from outside: an endpoint, a job, an event, a
screen. Prefer existing seams, and name the nearest existing test for each. One seam is ideal.
This is what the test-planner builds its checklist on.

## Open questions
| Question | Who decides | Blocks which Req |
|---|---|---|

## Vocabulary
Terms the sources use that an agent could misread, one line each. Skip if none.
````

Rules:

- Every row in Decisions maps to one id in `requirements.yaml`, and the reverse.
- No service names, file paths, contract items or PR split. If a source states one, record it as a constraint in the requirement's `source_text` and leave design to the planner.
- No active requirement or Test seam relies on a `blocked` requirement as if it were live. When several requirements decide one outcome, a line under Decisions says which wins.
- Anything in Open Questions has a `blocked` requirement, and no `blocked` requirement is missing here.
- No names, emails, phone numbers, IDs or amounts from real customers. Quote the rule, not the case.
