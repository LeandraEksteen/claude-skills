---
name: ping
description: Sets up a daily scheduled routine that sends "ping" to the cheapest model early in the morning, so the user's rolling usage window (for example 5 hours) starts before the workday and resets earlier instead of cutting them off mid-afternoon. Creates the routine in the user's own account, removes the connectors/tools it does not need, and checks the next run time. Use when someone says "set up the morning ping", "ping Claude at 6am", "start my Claude session early", "stop my usage resetting mid day", or "/ping". Also lists or changes an existing ping routine. Does NOT delete routines (that is done in the web UI).
user-invocable: true
argument-hint: "[HH:MM local time, default 06:00] [list|change]"
---

# Ping

Each user's Claude usage is counted in 5-hour sessions that start with their first message. A routine that
sends one tiny message early in the morning starts that session before work, so it resets at a predictable
time during the day. This skill creates that routine in **the user's own** Claude account; every person
runs it once for themselves (it cannot create routines in someone else's account).

## Configuration

Adjust these for your environment. Use whatever routine-management tool your environment provides; the
names below are the defaults.

| Setting | Default |
|---|---|
| Cheap model ID | `claude-haiku-5-5` |
| Default local time | `06:00` |
| Routines page | `https://claude.ai/code/routines` |
| Routine tool | `RemoteTrigger` (load with `ToolSearch("select:RemoteTrigger")`) |
| Scheduling skill | `/schedule` |
| Usage view | `/usage` |

## Critical — read first

- **One routine per user.** List the routines first. If one named `Morning ping` exists, offer to change it
  instead of creating a second.
- **Cheapest model and the word "ping" only.** Use the cheap model ID from Configuration, prompt exactly
  `ping`, no repository, and no connectors. Anything more uses more of the session the routine is meant to
  start.
- **Confirm the time in both zones.** Cron runs in UTC. Show the local time and the UTC time, and create
  only after the user says yes.
- **Never claim a delete.** Routines cannot be deleted from here. Point the user to the routines page.

## Process

### Step 1: Check what exists

Load the routine tool and call `{action: "list"}`. If a routine whose name starts with `Morning ping` exists,
show its schedule (in local time and UTC), model and `next_run_at`, and ask: "Change it, or leave it?" If the
argument was `list`, stop here.

### Step 2: Work out the time

- Time: the argument, or the default local time if none was given.
- Time zone: run `date +%Z` and read the IANA zone with
  `readlink /etc/localtime | sed 's#.*/zoneinfo/##'` (macOS) or `timedatectl show -p Timezone --value`
  (Linux). If neither works, ask the user.
- Convert the local time to UTC for a daily cron. Example: 06:00 in a zone at UTC+5:30 is 00:30 UTC, so the
  cron is `30 0 * * *`. For zones with daylight saving, tell the user the UTC hour moves twice a year and the
  routine must be changed then.
- Tell the user when their sessions will reset: start time, start + 5 h, start + 10 h.

### Step 3: Create it

Hand the creation to the scheduling skill/tool with a request like the following, filled in:

```text
Create a daily routine named "Morning ping (HH:MM <ZONE>)" with cron "<CRON>" (UTC) that sends the
prompt "ping" on model <cheap-model-id>. No repository, no MCP connectors, no tools needed.
```

The scheduler supplies the user's cloud environment and performs the create call. Let it show the
configuration and obtain the user's explicit yes before the create happens.

### Step 4: Remove what the server adds

The server attaches every connector the user has by default. Remove them with an update call:

```json
{"action": "update", "trigger_id": "<id from the create result>", "body": {"clear_mcp_connections": true}}
```

The server also fills in a default tool list. "ping" needs no tools, so leave it unless the user wants it
trimmed in the web UI.

### Step 5: Report

Show: the routine link (`<routines-page>/<id>`), the schedule in local time and UTC, and `next_run_at`
converted to local time. The scheduler may start a run a few minutes after the cron time; say so if
`next_run_at` differs from the requested time. Tell the user to check their usage view after the first run:
the reset time should be about 5 hours after the run.

## Examples

- `/ping`, no routine exists, zone UTC+5:30: 06:00 local is `30 0 * * *` UTC. Sessions would reset around
  11:00 and 16:00. After a yes, the scheduler creates it, connectors are cleared, and the report shows next
  run about 06:07 local.
- `/ping 07:30` with an existing routine at 06:00: show the existing one; the user says change it; the
  routine is updated to the new cron (`0 2 * * *` for 07:30 at UTC+5:30) with the same prompt and model.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Routine tool not found | Tool not loaded | Load it through tool search |
| Create fails on the environment | No cloud environment for this account | Open the web app once to create the default environment, then retry |
| Usage reset time did not move | The routine did not run, or its run does not count toward the session | `{action: "list_runs"}` on the routine; check the run happened and its time |
| Two ping routines | Created twice | Delete the extra one in the web UI (the skill cannot) |

## Rules

- List before creating; one ping routine per user.
- Cheapest model, prompt `ping`, no repository, no connectors.
- Show local time and UTC; create only after a yes.
- Clear the connectors after create.
- Never claim a routine was deleted.
