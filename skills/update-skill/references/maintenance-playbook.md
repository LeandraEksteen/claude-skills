# Maintenance playbook — diagnosis and fixes

Distilled from the team CONTRIBUTING guide and Anthropic's public guide to building skills
(https://docs.claude.com/en/docs/agent-skills). Bundled inside this skill because the team CONTRIBUTING
file lives above the skill folder and stops resolving once the skill is symlinked. When in doubt, the
repo's CONTRIBUTING guide is authoritative.

## Triggering diagnosis

| Symptom | Likely cause | Fix |
|---|---|---|
| Skill never loads for requests it should handle | Description too vague, or missing the verbatim phrases engineers actually type | Add specific trigger phrases in quotes; re-check against the WHAT + WHEN + triggers formula |
| Skill loads for unrelated requests | Description too broad, or overlaps another skill's territory | Narrow the WHEN clause; add a negative trigger (Do NOT use for Y — see /other-skill) |
| Skill loads but gives up partway, confused about scope | The body (not the description) is ambiguous about what it covers | Fix the Critical block or Step 1 framing, not just the description |
| Two skills both fire on the same phrasing | Overlapping descriptions, no negative trigger either way | Add a negative trigger to whichever skill is narrower in scope |

Test any trigger fix by phrasing the request 3-5 ways that should load it, and a couple that shouldn't,
before and after the change.

## The quality gate — every rule and its fix

Run from the team folder: `python3 scripts/check-skills.py <name>` (or the task-runner alias). It must
print OK.

| Rule | Means | Fix |
|---|---|---|
| folder-naming | folder not kebab-case | lowercase + hyphens + digits only |
| reserved-prefix | folder/name starts with claude/anthropic | rename (a structural change: confirm with the user first, since it changes the skill's identity) |
| no-readme | a README.md sits in the skill folder | delete it; move content to SKILL.md / references/ |
| missing-skill-md | no SKILL.md | shouldn't happen on an existing skill: check you found the right folder |
| skill-md-wrong-case | file is skill.md / Skill.md | rename to exact SKILL.md |
| frontmatter-missing | no --- frontmatter block | add it, opened and closed with --- |
| name-missing | no name: | add it |
| name-format | name: not kebab-case | fix |
| name-folder-mismatch | name: differs from folder | make identical: almost always a typo from a prior edit, not an intentional rename |
| description-missing | no description: | add it |
| description-too-long | over 1024 chars | tighten; move explanatory detail into the body instead |
| frontmatter-xml | < or > in a field other than argument-hint | use [placeholder] or backticks |
| skill-md-too-long | body over 5000 words | move detail into references/<topic>.md, grouped by topic |

If the target team has no validator script, say so plainly: you cannot lint there, so limit the fix to
what you can verify by hand (frontmatter shape, reference sync, README row).

## Reference sync — orphan check

A skill's references/ folder and its SKILL.md body must agree exactly:

1. List every file under references/.
2. Grep SKILL.md for a MUST-READ handoff pointing at each one:
   **You MUST read references/<name>.md before <action>. Do not improvise <thing>.**
3. Any file with no handoff pointing at it is an orphaned reference: either it is genuinely unused
   (delete it) or a handoff was dropped by mistake (add it back at the point of need).
4. Any handoff pointing at a file that doesn't exist is a broken handoff: either the file was deleted
   and the handoff should go too, or the file needs to be restored.
5. A passive pointer ("see references/foo.md for more") with no imperative trigger is a weak handoff:
   convert it to the MUST-READ form; don't leave both the old passive line and a new imperative one.

## README sync

The team README has a Skills table: one row per skill, naming what it does in a sentence or two.
It drifts when:

- The description changed but the row didn't (rewrite the row to match).
- A new skill was added but never listed (add the row: an unlisted skill is invisible to teammates).
- The skill was renamed or removed (update or delete the row to match).

## Content drift (commands, paths, tool names)

If a step references a specific command, file path, or tool that has since moved or been renamed elsewhere
in the repo or the team's tooling, update just that detail. This is still hygiene: the step's intent hasn't
changed, only a stale specific inside it. If the intent of the step needs to change, that's a feature
change: say so instead of quietly rewriting it under a hygiene label.

## When it's not hygiene

If the request is "make this skill also do X" or "add a step for Y", that changes what the skill does.
Name it as a feature change and make the edit as you would any other code change in this repo: write the
new step or behavior directly, then still run the gate and the README/reference sync above before shipping,
since those checks apply to every change regardless of why it was made.
