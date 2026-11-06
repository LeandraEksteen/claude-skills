# Checklist format

Loaded by Step 1 (writing `test-plan.md`) and Step 2 (the copies and the tracker comment). `test-plan.md`
goes in `<work-dir>`, beside `spec.md` and `requirements.yaml`.

## test-plan.md

````markdown
# PROJ-1234 — Test plan: <title>

Status: draft            # draft | approved. Set to approved only after the user approves in Step 2
Source: spec.md (approved <date>) | plan.md test matrix | Ticket as written
Environment: not yet set # run mode fills this: staging, each repo's branch and the commit under test
Scope: <what this plan checks and what it does not>   # from the Step 0 scope question; no case may go outside it
Summary: <N> cases, about <M> minutes for a full run, <n> high priority
Estimate basis: <M> = 3 min per case plus 15 for setup   # state how M was worked out, never invent it
Google Doc: <link>        # filled in when the plan is approved
Google Sheet: <link>      # filled in when the plan is approved
Copies: v1 <date> Doc <link>, Sheet <link>   # one entry per copy made; the latest is current
Test data: <the test accounts or setup the cases need, filled in by run mode>

## Cases

### TC-1 [high] Stalled signup triggers the reminder once
Covers: Req #1
Story: As a customer, when my signup has had no progress for 5 days, I get one reminder.
Preconditions: A test customer account with a signup started 5 days ago and not completed.
Steps:
1. Sign in to the customer site as that test customer.
2. Open the signup and confirm it shows as not completed.
3. Ask for the daily check to run (or wait for it), then open the inbox for the test customer.
Expected: One reminder email arrives with a link back to the signup.
Also check: The ops tool shows the reminder against the signup. No second reminder after a second run.
Unit-tested: yes (the trigger), no (the email content)
Status: pending          # pending | passed | failed | blocked | dropped
Result:                  # who, date, notes. Filled in as results are reported
````

Fields:

- **Id** `TC-N`. Append-only: never renumber, never delete. A dropped case keeps its id with
  `Status: dropped` and the reason in Result.
- **Heading priority** `[high]` or `[normal]`.
- **Covers** the `Req #` numbers it checks, or `non-goal: <the non-goal>`. Never empty.
- **Story** one line in the "As a ... when ... I ..." form.
- **Preconditions** the kind of test account and the state it must be in. Never a real customer.
- **Steps** a numbered list a tester can follow cold: which screen, what to click or type. No class names,
  endpoints or file paths.
- **Expected** one observable result, with where to see it (screen, email, ops tool, report).
- **Also check** side effects to look at: messages sent, statuses in the ops tool, records created or not. A
  value on no screen names the tool and the lookup, and the access goes in Test data.
- **Unit-tested** what the unit tests already cover, citing `UT-N` ids from the build skill's
  `pr-strategy.yaml` (never reuse `UT-` or `MC-` ids as case ids). Information only. Omit the line entirely
  when there is no matrix or `pr-strategy.yaml`: absent means not known yet, never "no", and "yes" needs a
  cited test.
- **Status** `pending`, `passed`, `failed`, `blocked` or `dropped`.
- **History** (optional, written by the spreadsheet import) earlier statuses and results of a retested case.
- **Result** for `passed`: "<name or role>, <date>". For `failed`: also what they saw instead. For `blocked`:
  why, and who can unblock. A retest keeps earlier results as a history line.

## Workflow coverage

(Only when a browser-verification skill with recorded workflows exists.) A table: case, the workflow that
reaches its preconditions (or `none`), and the gap. A `none` is a blocker for the run and has an Open Question.

| Case | Workflow | Gap |
|---|---|---|
| TC-1 | customer-sign-up | none |
| TC-3 | none | no returning-customer workflow |

## Open questions

A table: question, who decides, which case it blocks. A guess about behaviour belongs here, never in a case.

## Not tested here

Requirements the user ruled out of this plan, one line each or `Req 18, 19 and 22`, each with the reason. A
requirement listed here needs no case. A dropped case (`Status: dropped`) keeps its id but covers nothing, and
the Summary may count all cases or only those still run: say which, for example `13 cases (TC-12 and TC-13
dropped)`.

## Posting to the tracker

One comment, headed `Acceptance test plan — <KEY>`, with the environment, the summary line and then each case
as a checkbox line: `- [ ] TC-1 [high] <story> — Expected: <expected>`. Passed cases show `- [x]` followed by
who and when in brackets. Failed cases start with `- [ ] FAILED` and carry what was seen. Post with the
tracker connector's markdown content format. No bold inside table cells. After posting, read the comment back
once to check the checkboxes and tables rendered.

## Time estimate

The Summary line keeps the exact form `Summary: <N> cases, about <M> minutes for a full run, <n> high
priority`, because the lint recounts N and n. State the basis of M on the `Estimate basis:` line.

## Bug note

Title, the case id, the steps, the expected result, what happened, the requirement it breaks, the environment
and build. No personal data. Filed as a tracker bug linked to the ticket only on a yes.
