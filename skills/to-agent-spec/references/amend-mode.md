# Amend mode

Loaded when `/to-agent-spec <KEY> --amend` is run, when the user changes a decision after approval, or when a later planning or test-planning run surfaces a behaviour decision. Any behaviour-changing decision made while planning or testing goes back into the spec here, not only into the plan or the test cases.

## Steps

1. **State what changes and why**, in a sentence or two, citing who decided and when. Wait for a yes.
2. **Edit `spec.md` and `requirements.yaml` together.**
   - Ids are append-only: never renumber, never reuse an id for a different subject.
   - A blocked requirement that gets decided keeps its id: set its `status`, clear `blocked_on`, fill `decided_by`, and remove its Open Questions row.
   - If it ends `out-of-scope` or `dropped`, say so in `decided_by` and `supersedes`.
   - A new subject gets a new id. Update the Decisions row, Conflicts resolved and the precedence line.
3. Set `Approved: no`, then run `python3 <skill-dir>/scripts/epic-lint.py <workspace-root>/<name> --stage spec` and fix every ERROR.
4. Show the diff in plain words and ask "Approve the amended spec?". Only an explicit yes sets `Approved: yes`.
5. **Downstream refresh list.** Print every artifact that now disagrees with the spec, only those that exist:
   - the ticket description, and any posted test-plan comment
   - shared-document copies of the spec
   - `test-plan.md` cases (and any CSV export)
   - `plan.md` and `pr-strategy.yaml`

   Offer each refresh as its own opt-in (show the text, act only on a yes). After a ticket edit or comment, set `ticket_updated` and `ticket_content_sha` again (see ticket-creation reference § Freshness).
6. One line: if the workspace folder is invisible to the app's file pane, offer the scratchpad copy as in Step 5.
