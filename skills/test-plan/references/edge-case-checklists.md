# Edge-case checklists

Loaded when adding unhappy paths to a plan. This is the team's testing playbook, built up one real finding at
a time. Add an entry only when a bug, incident or review showed the case matters, and say where it came from.
Never pad a domain with guesses.

## Generic prompts (used when a domain has no checklist yet)

For each requirement ask:

- **Repeat.** Does doing it twice, or two people doing it at once, change the result?
- **Empty or missing.** What if a field, document or record is absent?
- **Boundary.** The exact limit, one below it and one above it (days, amounts, counts).
- **Late or out of order.** What if a step arrives after the next one, or after a timeout?
- **Already in flight.** What happens to records created before the change, and to ones part-way through?
- **Failure.** What if the other system is down or answers with an error? Is anyone told, is it retried, can it loop?
- **Permissions.** Who must not be able to do this, and are they stopped?
- **Notification.** Who is told, through which channel, and what if that fails?
- **Observable.** Can a tester see this outcome without engineering? If not, where (which tool, which lookup)?
- **Reversal.** Can it be undone, and what does undoing leave behind?

## How to add an entry

Under the right domain heading, add one line: the case, then `(source: <ticket, incident or PR>)`. Keep it to
a question a tester can act on.

## <domain-1, e.g. checkout>

- Boundary on a threshold: test one below, exactly at, and one above the limit, and check which date counts
  when a record has two candidate dates (created versus updated). (source: <ticket>)
- An automatic path that fails while a manual fallback exists: is the fallback offered, and is a duplicate
  task avoided? (source: <ticket>)
- Values read from a reporting tool may lag a save: wait for the refresh before judging a result, and note the
  typical lag per environment. (source: <ticket>)
- A bulk or re-run job: do a dry run first, compare its count with what the case expects, check a record it
  must skip, and check whether the effect reaches the end user (an email). (source: <ticket>)
- A paused or closed option: test the exempt path, the lookup that decides the exemption failing or pending,
  each boundary date (in a timezone west of UTC), the banner copy, and a prefilled link to a closed option.
  (source: <ticket>)
- Staging data is an anonymised copy and some stored fields can be random: a case that depends on such a
  field needs a record whose value the tester sets first. (source: <ticket>)
- A value inherited from an earlier record: test where the earlier record and the entered value disagree,
  since an agreeing pair proves nothing about which one won. (source: <ticket>)

## <domain-2, e.g. notifications>

_No entries yet._

## other

_No entries yet._
