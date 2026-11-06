# External prompt/config registry (optional)

The following pattern is worth keeping as an optional extension for any repo whose runtime behaviour depends on named items stored *outside the repo* (prompt registry, feature-flag service, remote config, CMS, translation platform):

**Problem.** A PR that adds or renames a name the code fetches at runtime has no effect (or fails, or falls back to manual handling) until the item exists in the external system *of that environment*. The merge deploys the code but not the item.

**When it applies.** The diff adds or changes a name passed to the registry fetch call, or a config entry naming a registry item. Detect it by diffing the config file and grepping changed source files for the fetch call. No new name: skip the step.

**Reference file should record (team fills in):**
1. A table of item kinds: registry name pattern, type, the label/version/stage the code reads, and how it is parsed. Include any quirks that corrupt items (for example, template engines that treat `{` and `}` as placeholders, so literal JSON braces in a prompt break formatting; list the allowed variables).
2. **Drafts.** The implementing agent writes each new item's full text to `<workspace-root>/<key>/state/registry-drafts.md`, one section per name, body in a fenced block. The orchestrator reads each draft against the format rules and the nearest existing item, fixes it, and the PR body carries the same drafts under a "Before merge: registry (manual)" collapsible block.
3. **Environments.** URL and project identifier per environment. Staging is set up at Step 7.5, before any staging test. Production is set up only when the user asks, and always before the PR merges when merging deploys; until then it stays in the summary's deploy notes.
4. **How to create the items.** Prefer the registry's API/CLI. If only a UI exists, drive it through a browser automation tool with the user's existing signed-in session (never sign in for them): show the user the list of names and the environment and get a yes once per environment; check whether the item already exists (if so, show the live text next to the draft and ask whether to add a new version rather than overwriting); create it; then verify on the item's page (labels/badges, first and last lines, variable counts); record "environment: done on <date> (names, version, labels)" in the drafts file and the PR body, keeping "Production: still to do" until it is.
5. **Smoke test.** After the PR is on staging, one real request exercising the new item should show it fetched (trace/log), and the documented failure message (for example "prompt fetch failed for '<name>'") means a missing name or label.

If your stack has no external registry, omit Step 7.5 and this reference entirely.
