# claude-skills

Generic, team-neutral Claude skills for turning a ticket into a spec, a plan and PRs, testing the result, and
keeping the skills themselves tidy. They work for one repo or several.

Placeholders such as `<workspace-root>`, `<issue-tracker>` and `<ci-system>` are left for you to fill in.
`to-agent-spec`, `build`, `implement`, `test-plan` and `ping` list theirs in a `Configuration` section at the
top of `SKILL.md`; `diagnosing-bugs` and `investigation-log` keep theirs in their reference files and intro.

## Skills

| Skill | What it does |
|---|---|
| [to-agent-spec](skills/to-agent-spec) | Turns tickets, PRDs, chat threads and discussion into one agreed `spec.md` + `requirements.yaml`. Owns the shared `epic-lint.py`. |
| [build](skills/build) | Turns a ticket or spec into a plan for one repo or several: contract (minimal for a single repo), requirements, PR strategy. Has a check mode. |
| [implement](skills/implement) | Executes an approved `build` plan for one repo or several, one subagent and worktree per PR. Never merges. |
| [test-plan](skills/test-plan) | Writes click-through acceptance cases for staging and tracks results to sign-off. |
| [diagnosing-bugs](skills/diagnosing-bugs) | Investigates a bug to a tiered root cause, then asks before fixing. |
| [investigation-log](skills/investigation-log) | Keeps a long multi-session investigation cheap to resume (INDEX.md, topics, log, forks). |
| [create-skill](skills/create-skill) | Scaffolds a new skill and runs the quality gate. |
| [update-skill](skills/update-skill) | Fixes trigger, gate, reference and README drift on an existing skill. |
| [ping](skills/ping) | Sets up a daily routine that starts the usage window early. |

## How they fit together

`to-agent-spec` -> `build` -> `implement`, with `test-plan` run against the same work folder. Each hands the
next its files in `<workspace-root>/<key>/` (`spec.md`, `requirements.yaml`, `contract.md`,
`pr-strategy.yaml`, `test-plan.md`). The other skills are standalone.

- `build` and `test-plan` call `to-agent-spec/scripts/epic-lint.py` (written as `<path-to-spec-skill>` in their
  text), so install those skills side by side.
- `epic-lint.py` needs PyYAML (`python3 -m pip install --user pyyaml`) or `ruby` on PATH.
- `create-skill` and `update-skill` run `scripts/check-skills.py` (below).

## No tracker?

`to-agent-spec`, `build`, `implement` and `test-plan` fall back to local tickets: a `ticket.md` per work item in
the workspace folder, keyed `LOCAL-<n>`. Each of those skills carries an identical
`references/local-tickets.md`; keep the four copies in sync.

## Quality gate

```bash
python3 scripts/check-skills.py            # all skills
python3 scripts/check-skills.py ping       # one skill
```

It checks folder and `name:` format, frontmatter, description length, angle brackets, a stray `README.md` in a
skill folder, and the 5000-word limit on `SKILL.md`.

## Install

Symlink each skill folder into `~/.claude/skills/`:

```bash
for s in skills/*/; do ln -s "$PWD/$s" ~/.claude/skills/"$(basename "$s")"; done
```

Skills that reference another skill (see above) expect it to be installed too.
