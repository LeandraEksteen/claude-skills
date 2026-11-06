# Contract check

Loaded by Step 5 (and by `--check`). Read every branch's diff against a fresh `origin/<base>`: `git -C <worktree> diff origin/<base>...HEAD`, or the hosted-code CLI's PR-diff for opened PRs. Evidence comes from the diff, never from the plan: every finding cites `repo:path:line` on the branch.

For each contract item, one row: item, producer evidence, consumer evidence, verdict (`match` / `mismatch` / `unchecked`), and for a mismatch the exact difference. A side missing from every branch is a finding ("C2 consumer not implemented"). Something you could not read (a subscriber in a repo with no checkout) is `unchecked`, never `match`.

Then check the set as a whole:

- **Unplanned crossings**: a new client call, endpoint, publish or subscribe in a diff that no contract item covers.
- **Other consumers**: for each changed endpoint or event, grep the path or event name across every local checkout in your organisation. A changed shape that breaks a caller outside the plan is the most severe finding.
- **Compatibility**: removed or renamed fields, endpoints, events or enum values; newly required request params; newly non-null response fields. And in each consumer: the tolerant read, toggle or error handling for the producer not being live yet, with a test.
- **Deploy order**: `merge_order` puts every producer before its consumers, or the consumer is proven tolerant.

## What counts as a match

One section per item kind. "Producer" and "consumer" follow the contract item.

**rest**

Producer side:
- Route exists for the verb and path (routes file or URL conf).
- Controller action permits every request param in the Shape and requires only those marked required (strong params or the serializer show this).
- Response contains every field in the Shape, with the stated type and nullability. Read the serializer, view or render call that the action actually uses.
- Status codes for the Errors listed.
- The API-doc request test covers the new shape, and the generated API doc in the diff contains it. Missing regeneration is a finding, not a mismatch of the contract.

Consumer side (the caller's client):
- Same verb and path, including version prefix (`v2/` versus `v3/`) and trailing segments.
- Request body keys spelled exactly as the Shape. Watch `snake_case` versus `camelCase` and symbol versus string keys.
- Every response field it reads exists in the Shape: search the diff for the parse/lookup calls and field accesses on the parsed response.
- Error handling: what the code does on each listed status and on timeout. A client that returns `nil` on failure passes the problem to its callers: follow one level up.
- Auth header and token config match how the producer authenticates.

**event**

Producer side:
- The publish call's event string equals the contract's event name exactly, including pluralisation and tense (`updates` versus `update`, `creates` versus `created`).
- The message class or hash has every payload key in the Shape. For callback-style messages the payload is model + id + URL; subscribers re-fetch, so the REST item carries the shape.
- It publishes in every code path the contract says (create and update, not only one), and after the transaction commits rather than inside it when the subscriber re-reads the record.

Consumer side:
- The subscribe call binds the same routing key the producer publishes. If the producer's name has a service prefix, confirm how the subscriber's binding matches it by reading the analog subscriber in the same repo.
- Handler reads only payload keys that exist; for callbacks, it re-fetches through the REST client.
- Handler is idempotent: the same message delivered twice does no double work.
- A handler that raises may dead-letter the message. Missing optional keys must not raise.

**ui-api** (frontend to API)
- The API-module function's method, path and body match the backend route and params.
- The type for the response matches the Shape; optional fields are optional.
- The component handles the old response shape (field absent) without crashing; a test shows it.

**config**
- The env var or config key is read by the consumer.
- Declared in the repo's keys manifest and sample env file, if it has them.
- Someone must set it per environment before deploy. This is always a deploy note, since no diff can prove it. Report it under "unchecked: needs a human".

## Severity (highest first)

1. A consumer outside the set breaks (other subscriber, other caller).
2. Contract mismatch between the two sides of the set.
3. Unsafe deploy order: consumer not tolerant and merge order puts it first.
4. Breaking change shipped as one step.
5. Missing test for the contract example or compatibility case.
6. Out-of-scope files, API docs not regenerated, base drift.
