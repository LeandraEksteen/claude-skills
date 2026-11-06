---
name: create-skill
description: Scaffold and validate a new Claude skill inside the shared skills repo, following the target team's contributing conventions and quality gate. Works for any team space in the repo; it asks which team rather than assuming. Creates the skill folder, writes SKILL.md with correct frontmatter, helps craft a trigger-rich description and a progressive-disclosure body, runs the team's skill validator until it passes, and lists the skill in the team README. Use when the user says "create a skill", "make a new skill", "scaffold a skill", "add a skill to the skills repo", or "write a skill for the team". Do NOT use to edit or maintain an existing skill (see /update-skill) or to install/link skills into a user's skills directory.
user-invocable: true
argument-hint: "<skill-name> [team] [what it should do]"
---

# Create a Skill

You are helping an engineer author a new skill that lands cleanly in the team's skills folder and passes the quality gate on the first pull request. Your job is to turn their idea into a correctly structured, well-triggered skill. Do not only create files: get the **description** and the **body** right, because those are what make a skill actually fire and actually work.

## Configuration

Where things live depends on the repo. In the `claude-skills` repo itself there is one team space:

| Item | Path |
|---|---|
| Skill folder | `skills/<name>/` (not `teams/<team>/skills/<name>/`) |
| Quality gate | `python3 scripts/check-skills.py <name>`, run from the repo root |
| Skills table | the repo-root `README.md` |
| Link into the user's skills directory | `ln -s "$PWD/skills/<name>" ~/.claude/skills/<name>` |

In a repo with several team spaces, use the team's own paths and ask which team (Step 1).

## Critical — read first

- **Work inside a clone of the shared skills repository.** New skills live at `teams/<team>/skills/<name>/` (adapt to the repo's real layout). If you are not in that checkout, stop and ask the user for the path.
- **Never assume the team.** The repo may hold several team spaces. Establish which one the new skill belongs to from the user's input, or by asking (Step 1), before creating anything. Every later path (the skill folder, the validator, the README) is under the team you settle on, and each team's tooling may differ.
- **Check which teams have the quality gate.** If the chosen team has no validator script or task runner yet, Steps 5 and 8 (gate, link) cannot run. Say so plainly and treat the work as folder scaffolding until that team adds the tooling. Never silently skip them and never claim the gate passed.
- **Folder name is kebab-case** (lowercase letters, digits, hyphens only) and must **exactly match** the `name:` in the frontmatter. The file must be named `SKILL.md`, exact case; `skill.md` is wrong.
- **No `README.md` inside a skill folder.** Per-skill docs go in `SKILL.md` or `references/`.
- **Everything a skill references must live inside its own folder.** Skills are symlinked into the user-global skills directory (for example `~/.claude/skills/<name>`), so any `../` path (for example to a team `CONTRIBUTING.md`) breaks once linked. Bundle what the skill needs. Never point `SKILL.md` above its own directory.
- **Never name a skill with a `claude-` or `anthropic-` prefix** (reserved).
- **Run the gate before you call it done**, and **do not commit or open a PR unbidden**. Offer it.

## Process

### Step 1 — Name it and pick the team

Settle on a kebab-case `name`, then establish the team space. Do not assume it.

- List the team folders (for example `ls teams/`) and take the one the user named.
- If they did not name one, ask. Only skip asking when there is exactly one team folder, or the user is plainly working inside a single team's checkout.

The skill's home is `teams/<team>/skills/<name>/`. Check nothing already exists there. Hold on to `<team>`, because every later step is under it.

### Step 2 — Write the description (the highest-leverage step)

The `description` is the only thing Claude sees when deciding whether to load the skill. Get it wrong and the skill never triggers, or triggers on everything. Use the formula:

> **[What it does]** + **[When to use it]** + **[verbatim trigger phrases an engineer would say]**

Keep it under 1024 characters, use **no `<` or `>`** (these are only allowed in `argument-hint`), and add a negative trigger (`Do NOT use for Y — see /other-skill`) when it could be confused with an existing skill.

**You MUST read `references/skill-conventions.md` before writing the description and body. Do not improvise the description formula, the body structure, or the team conventions. They are the rules the reviewer and the gate check against.**

### Step 3 — Scaffold the folder and SKILL.md

Create `skills/<name>/SKILL.md` from the house skeleton.

**You MUST read `references/skill-template.md` before creating the files, and copy its skeleton. Do not hand-roll the frontmatter or the section layout.**

Set `user-invocable: true` and an `argument-hint:` if the skill is meant to run as a slash command (most team skills are).

### Step 4 — Write the body

Follow the structure from `references/skill-conventions.md`. Keep `SKILL.md` **under 5000 words**. When it grows past that, move detail into `references/<topic>.md` (kebab-case, grouped by topic). At every handoff to a reference, place an explicit imperative trigger immediately before the step that needs it:

> `**You MUST read references/<name>.md before <action>. Do not improvise <thing>.**`

Put hard rules in a `## Critical` block at the **top**, not buried mid-body. Be specific and actionable: exact commands, not "validate the data". Bundle a deterministic `scripts/` helper for any rule that must hold exactly.

### Step 5 — Run the quality gate

From the team folder, run:

```bash
python3 scripts/check-skills.py <name>
```

It must print `OK`. Fix every violation and re-run until clean. `references/skill-conventions.md` has the full rule list and the fix for each. If the repo has no CI for skills, this gate is the only automated check. If the target team has no validator, say so: you cannot lint there until the team adds one. Do not pretend it passed.

### Step 6 — List it in the team README

Add a row to the Skills table in the team's `README.md` (what it does, in one line). A skill that is not listed is invisible to teammates.

### Step 7 — Test it

- **Triggering:** phrase the request 5 or more ways that *should* load the skill, and a few that *should not*.
- **Functional:** run it end to end against a real task; confirm it calls the right tools in the right order.

If it never triggers, the description is too vague: add verbatim phrases. If it triggers on everything, narrow the scope or add negative triggers.

### Step 8 — Link and ship

To use the skill immediately, run the repo's link task (for example `task skills` from the team folder, which symlinks it into the user's global skills directory; restart the agent to see it). Then **offer** to commit and open a PR. Do not do it unprompted. Never use `--no-verify` or force-push.

## Examples

- **"make a skill that audits our RBAC config"** → confirm name `rbac-audit` and the team; draft a description with triggers ("audit RBAC", "check permissions config"); scaffold from the template; write a Process plus Troubleshooting body; run the gate; add the README row; offer the PR.
- **"add a skill to the skills repo for drafting release notes"** → name `release-notes`; same flow.

## Troubleshooting

| Gate says | Cause | Fix |
|---|---|---|
| `name-folder-mismatch` | `name:` differs from folder name | Make them identical (kebab-case). |
| `frontmatter-xml` | `<` or `>` in a field other than `argument-hint` | Use `[placeholder]` or backticks. |
| `description-too-long` | over 1024 chars | Tighten; move detail into the body. |
| `skill-md-too-long` | body over 5000 words | Move detail into `references/`. |
| `no-readme` | a `README.md` in the skill folder | Delete it; put the content in `SKILL.md`. |
| `skill-md-wrong-case` | file is `skill.md` or `Skill.md` | Rename to exact `SKILL.md`. |

## Rules

- kebab-case folder equals `name:`; exact `SKILL.md`; no `README.md` in the folder.
- Everything referenced lives inside the skill folder (no `../`).
- Description is WHAT + WHEN + verbatim triggers, under 1024 chars, no angle brackets.
- The gate must pass, and the README must be updated, before shipping.
- No side effects (commit or PR) without the user's say-so. No `--no-verify`, no force-push.
- Identifiers are fine in skills; never bake in personal or sensitive data. (Adapt to your data domain: customer records, patient records, and so on.)
