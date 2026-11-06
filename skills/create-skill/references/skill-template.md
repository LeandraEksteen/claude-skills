# SKILL.md skeleton — copy this

Copy the block below into skills/<name>/SKILL.md and fill it in. Replace every [...]. Delete sections
the skill doesn't need (Prerequisites, Troubleshooting, and Rules are optional; Process + a worked Example
are usually load-bearing). Keep the body under 5000 words.

Frontmatter rules: `name` is kebab-case and identical to the folder name; `description` follows the
WHAT + WHEN + triggers formula, at most 1024 chars, with no < or >; `argument-hint` is the one field where
<arg> syntax is allowed. Drop `user-invocable`/`argument-hint` if the skill isn't a slash command.

````markdown
---
name: [kebab-case-name-matching-folder]
description: [What it does]. Use when the user [WHEN] — "[trigger phrase]", "[trigger phrase]", "[trigger phrase]". Do NOT use for [Y] — see /[other-skill].
user-invocable: true
argument-hint: "<primary-arg> [optional-arg]"
---

# [Skill Name]

[One or two sentences: who you are in this skill, what you're doing, the high-level approach.]

## Critical — read first

- [Non-negotiable #1 — the thing that breaks the skill if skipped.]
- [Non-negotiable #2.]

## Prerequisites

- [Access / token / state the user must have before this runs. Say how to check it. Omit if none.]

## Process

### Step 1 — [name]

[Specific, actionable instructions. Exact commands where possible.]

### Step 2 — [name]

[If this step needs a reference:]
**You MUST read references/[name].md before [action]. Do not improvise [thing].**

### Step 3 — [name]

[...]

## Examples

- **"[a real phrasing the user would type]"** -> [what the skill does, start to finish, in one line].

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| [error] | [why] | [what to do] |

## Rules

- [Recap of the Critical non-negotiables, one line each.]
````

## Folder layout to create

skills/<name>/
  SKILL.md            # required
  references/         # optional: detail loaded on demand (kebab-case, by topic)
    <topic>.md
  scripts/            # optional: deterministic validation / helpers
  assets/             # optional: templates, fixtures

Do not add a README.md inside the folder. Anything SKILL.md references must live under this folder:
no ../ paths, because the skill is symlinked into the user's global skills directory.
