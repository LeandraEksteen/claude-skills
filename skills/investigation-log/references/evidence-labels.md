# Evidence labels

Every claim in a topic file, the log and the shared doc carries one label.

| Label | Use when | Required with it |
|---|---|---|
| `[verified: <pointer>, <date>]` | You read it yourself from code, data or a primary source | Pointer: `repo@sha path:line`, a saved query or SQL, a URL to the primary page. Date. |
| `[inferred: <basis>]` | Reasoned from verified facts, or relayed from a source you did not check | The basis: which facts, or which source and who read it |
| `[proposal]` | An idea, recommendation or design choice, not a fact | None; never mixed into a findings list |

## Rules

- **Agent-read claims are `inferred`.** A sub-agent or fork says "the code does X": label it `inferred:
  read by <agent>, not spot-checked`. It becomes `verified` only after you read the pointer yourself.
- **Vendor and marketing claims are `inferred`** (basis: the vendor page), even when quoted exactly.
- **Meeting notes, machine summaries and chat are `inferred`** until checked against the primary source.
- **Check before promoting.** Open the pointer, confirm it says what the claim says, then change the label
  and add your date. Log the change.
- **Corrections are loud.** When a verified claim turns out wrong, fix it in the topic file, add a log line
  naming the old claim and the cause, and update every shared-doc sentence that repeated it (use the
  section map in INDEX).
- **Counts and numbers** carry the query, the filter and the date. A number without them is `inferred`.
- **Proposals stay in the Proposals list** and are written as proposals in the shared doc ("we propose").
- **Sources stay factual.** Record what a source is and when it was read. Do not put opinions about why a
  source was rejected into topic files or the doc; that goes in the log.
- **No personal data** in any label, pointer or quote.
