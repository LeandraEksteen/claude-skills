---
name: update-skill
description: Maintains an existing skill in the shared skills repo. Fixes a description that won't trigger (or over-triggers), re-runs the quality gate and clears its violations, keeps references/ free of orphans with MUST-READ handoffs in sync with the body, and syncs the team README row. Use when the user says "update this skill", "fix the skill trigger", "this skill isn't firing", "the skill triggers on everything", "sync the skill docs", "re-run the skill gate", "the README row is stale", or "clean up this skill". Scoped to hygiene and upkeep only. Do NOT use to add new capabilities, steps or integrations to a skill's behavior (that is a feature change, treat it as a normal edit). Do NOT use to scaffold a brand-new skill (see /create-skill).
user-invocable: true
argument-hint: "<skill-name> [team] [what's broken]"
---

# Update a Skill

You are maintaining a skill that already exists in the shared skills repo. Your job is narrow: restore or tighten something that has drifted (a trigger, the gate, a stale reference, a stale README row) without touching what the skill actually does. If the ask is a behavior change, say so and stop treating it as maintenance.

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

- **Hygiene only.** Fix triggers, gate violations, orphaned or stale references, and README drift. If the user wants new steps, a new integration, or different behavior, tell them plainly that this is a feature change, not an update-skill run. They (or you, working normally) edit `SKILL.md` directly, the same as any code change. Do not force this skill's frame onto that work.
- **Work inside a clone of the shared skills repository.** If you are not in that checkout, stop and ask for the path.
- **Never assume the team or the skill's location.** Several team spaces may exist. Find the skill first (Step 1) rather than guessing a team folder.
- **Everything the skill references must stay inside its own folder.** Skills are symlinked into a user-global skills directory (for example `~/.claude/skills/<name>`); a fix that adds a `../` path breaks once linked, exactly as at creation time.
- **Change only what's broken.** Do not rewrite sections that work, rename the skill, or restructure the body as a side effect of fixing one thing. Each of those is its own change.
- **Run the gate before calling it done**, and **do not commit or open a PR unbidden**. Offer it.

## Process

### Step 1 — Find the skill

Locate it: `find teams -maxdepth 3 -type d -name "<skill-name>"` (or take the team the user already named; adapt to the repo layout). If it is not under a `skills/` folder in any team, stop: this skill maintains existing skills, it does not create them (`/create-skill` does). Read its current `SKILL.md` and list its `references/` folder in full before touching anything.

### Step 2 — Diagnose what's actually wrong

**You MUST read `references/maintenance-playbook.md` before diagnosing or fixing anything. Do not improvise the gate's rule-to-fix mapping, the orphaned-reference check, or the triggering diagnosis. They exist so you do not guess at a fix that does not match the actual symptom.**

Match the complaint to one of: triggering (never fires, or fires on everything), a gate violation, an orphaned or missing MUST-READ reference handoff, or a stale README row. If the user did not say what is broken, ask, or run the gate first (Step 3) and let its output narrow it down.

### Step 3 — Run the quality gate

From the team folder:

```bash
python3 scripts/check-skills.py <name>
```

Fix every violation it reports using the table in `references/maintenance-playbook.md`. If the target team has no validator, say so. You cannot lint there, so limit yourself to the manual checks in Step 4 and do not claim the gate passed.

### Step 4 — Fix the specific thing

- **Trigger fix:** rewrite only the `description` field using the WHAT + WHEN + verbatim-triggers formula. Do not touch the body unless the body itself is what is misleading Claude about when to load.
- **Reference sync:** every `references/*.md` file must have exactly one MUST-READ handoff pointing at it from `SKILL.md`; every MUST-READ handoff must point at a file that exists. Delete orphaned reference files (nothing points at them) or orphaned handoffs (they point at a file that is gone). Do not leave either side dangling.
- **README sync:** if the description or what the skill does changed, update its row in the team README to match. If the row is just missing, add it.
- **Content drift:** if the body names a command, path or tool that has since changed elsewhere in the repo, update the reference, but only the drifted detail, not the surrounding step.

### Step 5 — Re-test

- **Triggering:** if you changed the description, phrase the request 3-5 ways that should (and a couple that should not) load the skill, and confirm the change actually fixes it.
- **Functional:** if you changed a Process step or a reference, run the skill once end to end to confirm it still calls the right tools in the right order.

### Step 6 — Offer to ship

Re-run the gate once more to confirm it is still clean. Then **offer** to commit and open a PR. Do not do it unprompted. Never use `--no-verify` or force-push.

## Examples

- **"`/some-skill` isn't triggering when I paste a monitoring link"** → read its `SKILL.md`, check the description for a missing trigger phrase, add it, re-run the gate, confirm with a few test phrasings.
- **"the create-skill README row is wrong, it says it only handles one team"** → read the current description, rewrite the README row to match; no `SKILL.md` change needed.
- **"can you make some-skill also handle staging queues"** → this is a feature change, not maintenance; say so and make the edit as a normal change, not through this skill's gate-and-sync frame.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Gate still fails after a description edit | over 1024 chars, or stray `<`/`>` | tighten; use `[placeholder]` or backticks |
| A `references/*.md` file nothing points to | handoff was removed from `SKILL.md` but the file was not | delete the file, or add back its MUST-READ handoff if still needed |
| `SKILL.md` has "see references/x.md" with no trigger | passive pointer instead of MUST-READ | convert to the imperative form; do not duplicate the content |
| README row does not match current behavior | description changed, row did not | rewrite the row in one line |
| Skill still mis-triggers after the fix | body (not just description) is confusing Claude | check Step 4's body note before editing the description again |

## Rules

- Fix the reported symptom only: no new steps, sections or capabilities as a drive-by.
- The gate must pass before calling it done.
- Every reference has exactly one MUST-READ handoff; no orphans in either direction.
- The README row matches current behavior.
- No side effects (commit or PR) without the user's say-so. No `--no-verify`, no force-push.
- A request to change what the skill *does* is a feature change: name it as one, do not route it through this skill.
