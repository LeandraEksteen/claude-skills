# Skill conventions — the judgment rules a linter can't catch

Distilled from the team CONTRIBUTING guide and Anthropic's guide to building skills.
This file is bundled inside the skill because the team CONTRIBUTING file lives above the skill folder and
stops resolving once the skill is symlinked. When in doubt, the repo's CONTRIBUTING guide is authoritative.

## The description — get this right or nothing else matters

It is the only thing Claude sees when deciding whether to load the skill.

**Formula:** `[What it does] + [When to use it] + [verbatim trigger phrases an engineer would say]`

Rules the gate enforces: at most 1024 characters; no `<` or `>` (allowed only in `argument-hint`); the name
has no `claude-` or `anthropic-` prefix.

### Good

description: Manages project-tracker workflows including sprint planning, task creation, and status tracking. Use when user mentions "sprint", "tracker tasks", "project planning", or asks to "create tickets".

description: Analyzes design files and generates developer handoff docs. Use when user uploads .fig files or asks for "design specs", "component documentation", or "design-to-code handoff".

### Bad

description: Helps with projects.                         # too vague: triggers on everything or nothing
description: Creates sophisticated documentation systems.  # no WHEN, no triggers: Claude has no signal
description: Implements the Project entity model.          # technical, no user-language triggers

### Tips

- Use the verbatim phrases an engineer would actually type ("deploy to prod", "why is X failing").
- Mention file types when relevant (.fig, .sql, .har).
- When two skills could be confused, add a negative trigger: `Use for X. Do NOT use for Y — see /other-skill.`

## Body structure

Load-bearing sections only. Every sentence costs tokens on every invocation.

# Skill Name
Brief framing: who you are, what you're doing, the approach.

## Critical — read first      (high-stakes non-negotiables, at the TOP)
## Prerequisites              (only if it needs access / tokens / state)
## Process                    (the step-by-step workflow, the meat)
### Step 1 ... ### Step 2 ...
## Examples                   (1-2 concrete worked examples)
## Troubleshooting            (common error -> cause -> fix)
## Rules                      (non-negotiables, recapped at the end)

Not every skill needs every section. Be specific and actionable: exact commands, not "validate the data".
Put hard rules in a Critical block at the top, never buried in step 7. Where a rule must hold exactly,
bundle a deterministic script and call it from SKILL.md; code is deterministic, prose isn't.

## Progressive disclosure — when to split into references/

Keep SKILL.md under 5000 words (gate-enforced). Past that, move detail into references/<topic>.md.

- To references/: API/curl/SQL/query templates, long lookup tables, rarely-needed fallback phases,
  setup/config procedures.
- Stays in SKILL.md: the flow followed on every invocation, the Critical rules, and the 1-2 sentences
  saying when to open each reference.

Name reference files kebab-case, grouped by topic (one tool / one phase / one decision tree per file), not
by step number.

### The MUST-READ handoff rule

When a step delegates real detail to a reference, put an imperative trigger immediately before that step:

**You MUST read references/<name>.md before <action>. Do not improvise <thing>.**

Convert, don't duplicate: when you move a block out, replace its old passive pointer with the MUST-READ
trigger; never leave both (wasted words, and the gate counts them against the 5000-word ceiling). Avoid
"see references/foo.md" with no signal about when to read it.

## Team conventions (layer on top of the universal guide)

These are example house rules. Another team's CONTRIBUTING guide may diverge. When the new skill targets a
different team, read that team's CONTRIBUTING guide and prefer it where it differs. Replace the list below
with your organisation's own rules.

- Slash-command invocation. Set `user-invocable: true` and an `argument-hint:` so the UI shows the args.
- Cross-skill references. Delegate with the slash prefix in the body so it's visible: "Run /other-skill."
- Tool/connector gating. A skill depending on an external connector (issue tracker, chat, BI, observability)
  must check it's connected before relying on it, and say plainly when it's unavailable. Never report an
  action done when its tool was absent.
- Opt-in for anything that changes the world. Filing a ticket, opening a PR, posting outside an existing
  thread: offer, don't do it unbidden. Reporting what you found and did not do is fine.
- Identifiers yes, personal data never. Record ids are fine; names, emails, phone numbers, government ids,
  dates of birth and addresses are not. (Adjust to your data-sensitivity rules.)
- No --no-verify, no force-push. If a hook fails, escalate to the user.

## The quality gate — every rule and its fix

Run from the team folder: `python3 scripts/check-skills.py <name>` (or the task-runner alias). It must
print OK. Rules:

| Rule | Means | Fix |
|---|---|---|
| folder-naming | folder not kebab-case | lowercase + hyphens + digits only |
| reserved-prefix | folder/name starts with claude/anthropic | rename |
| no-readme | a README.md sits in the skill folder | delete it; content goes to SKILL.md / references |
| missing-skill-md | no SKILL.md | create it |
| skill-md-wrong-case | file is skill.md / Skill.md | rename to exact SKILL.md |
| frontmatter-missing | no --- frontmatter block | add it, opened and closed with --- |
| name-missing | no name: | add it |
| name-format | name: not kebab-case | fix |
| name-folder-mismatch | name: differs from folder | make identical |
| description-missing | no description: | add it |
| description-too-long | over 1024 chars | tighten |
| frontmatter-xml | < or > in a field other than argument-hint | use [placeholder] or backticks |
| skill-md-too-long | body over 5000 words | move detail to references/ |

## Testing before a PR

1. Triggering: 5-10 phrasings that should load it, 5 that shouldn't.
2. Functional: run end to end against a real task; right output, right tools, right order.
3. Baseline (optional): same task with and without the skill. Fewer back-and-forths or failed calls?

Iterate: never triggers -> description too vague, add phrases. Triggers on junk -> too broad, add negative
triggers. Claude ignores mid-skill instructions -> too verbose or buried, move detail to references,
surface Critical rules at the top.
