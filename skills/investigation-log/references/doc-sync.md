# Syncing a shared findings doc

The doc is for sharing. The notes are for working. Keep them apart.

## Record the link once

In `INDEX.md` under "Shared doc": the link, and a section map (doc section to `topics/<area>.md`). Update
the map whenever the user adds or renames a doc section.

## Before editing the doc

- **Read only the section you are about to change**, not the whole doc. If the doc tool cannot read one
  section, read the smallest unit it allows and note the cost in the log.
- Edit only what the user asked for. Do not add sections, tables or summaries unprompted. If you think
  something should be added, say so and ask first. The user trims additions, so extra content costs them time.
- Decisions that are parked or declined in INDEX stay out of the doc unless the user asks for them.

## Writing for the doc

- Findings keep their label meaning: write verified facts as facts with the source named; write inferred
  claims as "reportedly" or "per [source]"; write proposals as "we propose".
- No meta-commentary about rejected or unreliable sources, and no process notes ("a sub-agent read this").
  That belongs in `log.md`.
- No personal data.

## After editing

- Append a log line: what changed, which doc section, which topic file it came from.
- If a correction touches a verified claim, update every doc sentence that repeated it, using the section map.
- Tell the user what you changed and where, in a line or two. Never share or publish the doc yourself.
