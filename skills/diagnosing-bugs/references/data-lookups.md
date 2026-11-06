# Data lookups

Read-only queries against the data warehouse to count or inspect affected records. Used in Step 3.

## Where

- Use the <BI/warehouse connector>. If it is absent, say so and ask the user for the data; never report a
  count you did not run.
- Production data is in <warehouse>, reached through <BI tool> (database id <id> at last use). Confirm the
  id by listing databases rather than trusting this file.
- Schemas seen in use: <list>. Find tables with `information_schema.tables` and columns with
  `information_schema.columns` before writing a query. Do not guess table names.

## Rules

- Read-only. SELECT only. Never write, and never use the lookup to change a record.
- Identifiers and amounts only. Select ids, statuses, flags, dates and amounts. Never select names, emails,
  phone numbers, government ids, dates of birth, addresses or bank details, and never paste them into chat,
  notes or drafts.
- The warehouse is usually a delta-loaded or otherwise lagging copy of the live database; some write paths
  may never sync (see known-footguns.md). State the freshness caveat when a count matters, and prefer the
  code path's own source when they disagree.
- Check the column is real. Before trusting a flag or amount, confirm in the code which table the
  application reads it from and that something writes it. A same-named column on another table may never be
  populated.
- Join checks. An empty join usually means the wrong key or table, not "no rows". Check the join separately
  before concluding.
- Show your count. Give the query (without personal data) and the number, so the user can rerun it.
  Hand-counted numbers are labelled as approximate.
