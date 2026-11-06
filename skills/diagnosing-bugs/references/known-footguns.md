# Known footguns

Recurring root-cause classes already seen on this team. Check these before forming a hypothesis. A match is
a first hypothesis to verify, not a conclusion. Add a new entry when a root cause is a class likely to
recur, and only with the user's say-so.

## <Short name of the bug class>

- **Symptom:** what the reporter or the tests show.
- **Cause:** the underlying mechanism.
- **Check:** how to confirm or rule it out in code or data (grep targets, which source to compare).
- **Fix shape:** the general direction of the fix (not a specific patch).

## Example 1: bulk write skips change-tracking column

- **Symptom:** data correct in the primary database but stale or missing in the reporting copy.
- **Cause:** bulk or column-level writes (for example ORM `update_all` / `update_column`) do not bump the
  `updated_at` column that an incremental sync relies on, so the row is never re-synced.
- **Check:** grep the write path for those methods on the affected model; see whether `updated_at` is set in
  the same call; see whether a lint rule that guards this was disabled.
- **Fix shape:** set the timestamp in the same write, or use a normal update.

## Example 2: hidden form field still submits a value

- **Symptom:** a user is recorded as having requested a value for a feature that was turned off for them.
- **Cause:** the field is not rendered when a flag is false, but its state is still prefilled, still counted
  by validation and still sent on submit.
- **Check:** where initial values are built and whether they read the flag; what the submit payload sends;
  whether the backend validates the flag too.
- **Fix shape:** zero the value when the flag is off, force it on submit, and reject it on the server.

## Example 3: two sources of truth for one flag

- **Symptom:** the front end and the backend disagree about whether a feature is on for an entity.
- **Cause:** one side reads a live service, the other a synced copy, and the flag may live on more than one table.
- **Check:** find which source each side reads and when the sync last wrote it.
- **Fix shape:** one authoritative source, or validate on the backend too.

## Example 4: a judgment re-derived in several places

- **Symptom:** the same yes/no decision gives different answers in different screens, jobs or exports.
- **Cause:** each place recomputes the decision from its own inputs and the copies drifted.
- **Check:** grep every place that computes it and compare inputs and conditions.
- **Fix shape:** decide once where the authoritative signal is in scope and pass the decision along as data.
