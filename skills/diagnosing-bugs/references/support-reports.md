# Support reports

A support or QA form/bot posts a structured potential-bug report in <support-channel>, tagging <team>.
A ticket in <issue-tracker> may be created by an existing automation; this skill never creates or touches it.

## Template fields and how to use them

| Field | Use |
|---|---|
| Severity | Sets urgency; note it in the reply |
| Was this working before | If yes, check recent merges and deploys touching the path (git log) |
| Expected / Actual behaviour | The symptom to explain; restate it in Step 1 |
| Steps to recreate | Reproduce in code or with read-only data where possible |
| Customer impact | Blast radius for the reply |
| Workaround status | Pass on in the reply; do not invent a workaround |
| Support-desk ticket link | Ignore. Out of scope, never read or write |
| Affected record ids / customer ids | Look up the records read-only; identifiers only, never copy personal data out |

If a field is empty and matters, ask the user or list it under "Not verified". Do not guess it.

## Reading the thread

Read the whole thread with the chat connector (read-thread), not just the first message: replies often carry
timeboxes, extra record ids or corrections. A user timebox ("give it an hour") applies to the investigation.

## Reply draft

Draft for the same thread, plain and short, for non-engineers:

1. What was found: root cause in one or two sentences, with the tier word (Confirmed, Probable or Candidate).
2. Fix status: not started, in progress, PR open (link), or deployed.
3. What support should do or tell the customer, and any data that needs correcting (ids only).
4. What is still unknown, if the tier is not Confirmed.

Show it in chat. Send with the chat connector only after an explicit yes to that draft, as a reply in the
thread. If the connector is absent, say nothing was sent and hand over the text.
