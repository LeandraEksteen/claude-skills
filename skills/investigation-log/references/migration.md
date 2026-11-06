# Migrating a large notes file into the layout

Propose first. Change nothing until the user approves the proposal.

## 1. Survey without reading it all

- `wc -l <notes>` and `grep -n '^#' <notes>` for the section map. Read only the headings, the first lines
  of the goal, decisions and open-question sections, and the tail of the log section.
- Do not read the whole file. If a section's destination is unclear, read that section only.

## 2. Write the proposal (to a scratchpad or `<slug>/migration-proposal.md`, never over the original)

- **Section to destination table**: each notes section maps to `INDEX.md` (goal, constraints, decisions,
  parked, open questions, pointers), a named `topics/<area>.md`, or `log.md`. Group related sub-sections
  into one topic per area, not one file per sub-section.
- **Draft `INDEX.md`**: filled from the template, at most about 100 lines, including a STATE block.
- **Log lines**: dated entries pulled from the old log section and from "read on <date>" headings.
- **Labels**: list claims that carry no evidence label. Propose `inferred` for them, never `verified`,
  unless a pointer is already present.
- **Risks**: sections you did not read, claims that may be stale, links to check.
- Note how much the next resume would read: the index size versus the original size.

## 3. After approval

- Copy, do not move. The original file stays untouched until the user confirms the new layout.
- Create the files, run `python3 scripts/check-index.py <slug-folder>` (bundled with this skill), fix
  anything it reports.
- Add a log entry: migrated from `<path>`, date, what was split.
- Add the memory pointer (references/memory-and-tokens.md).
- Migrated topic files keep source text verbatim, so most claims start unlabelled. Put a banner at the top
  of each ("migrated, unlabelled claims are inferred") and add a `## Summary` section. Label claims
  properly, topic by topic, when a topic is next touched; do not relabel everything in one pass.
- Tell the user the original can now be archived, and ask before touching it.
