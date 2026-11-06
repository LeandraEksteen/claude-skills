# Memory pointer and token discipline

(The memory pointer part applies only where the agent has a persistent memory system with an index file;
otherwise skip it or point to whatever the team uses, for example a pinned note.)

## Memory pointer

The auto-memory entry points at the index. It never copies findings, decisions or the STATE block.

```markdown
---
name: investigation-[slug]
description: "[one line: what the investigation is, so recall can decide relevance]"
metadata:
  type: project
---

Investigation log: `[root]/[slug]/INDEX.md`. Read that file first on resume (skill: /investigation-log).
Shared doc: [link, or none].
**How to apply:** do not re-derive from memory; open INDEX.md. This entry is a pointer, not a copy.
```

Check for an existing entry for the slug first and update it. Add one line to the memory index
(`MEMORY.md` or equivalent). If a memory entry already holds copied content (decisions, in-flight lists),
propose trimming it to the pointer and moving anything missing into INDEX.md. Do not delete without asking.

## Token discipline

- Resume: `INDEX.md` only. Then at most one topic file per question.
- Search before reading: `grep -n '<term>' <root>/<slug>/log.md <root>/<slug>/topics/*.md`, then read the
  matching lines with an offset and limit.
- Never re-read the shared doc to answer a question; the topic file holds the content. Read a doc section
  only to edit it.
- Fan-out reading (several files, repos or sources) goes to read-only agents. Where the harness allows,
  set an explicit cheaper `model` on those agents, and have each write labelled output to `forks/` rather
  than returning a large dump. Keep synthesis and judgment in the main session.
- Checkpoint before the context grows large, not after. A fresh STATE block means a compaction loses nothing.
- "Large" means about 300k tokens, not the 97% auto-compact point. Past that, every turn re-reads the whole
  context, so cost grows with turns times context. Long investigations observed averaged several hundred
  thousand tokens of context over hundreds to a thousand-plus turns. At about 300k, or at each milestone,
  rewrite STATE and tell the user to run `/compact`.
- Query results are context too. When querying a database, aggregate in the query (`COUNT`, `GROUP BY`) and
  list only the columns you need. Use `LIMIT` of 20-50 unless the full set is the point. When you need a
  long result, save it to a file and `grep` it. Do not let it sit in context.
- Read wiki pages and shared docs once into the topic file, then work from that file. Do not read the source
  again.
- Keep `INDEX.md` near 100 lines: when it grows, move detail into a topic file and leave a one-line pointer.
