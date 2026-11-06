#!/usr/bin/env python3
"""Check an investigation folder's INDEX.md: size, required sections, STATE block.

Usage: python3 check-index.py <investigation-folder>
Exit 0 and print OK when clean; exit 1 and list problems otherwise.
"""
import re
import sys
from pathlib import Path

MAX_LINES = 120
MAX_STATE_LINES = 10
SECTIONS = [
    "STATE", "Goal", "Constraints and stance", "Decisions made", "Parked",
    "Open questions", "Shared doc", "Forks / side sessions", "Topics", "Pointers",
]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    folder = Path(sys.argv[1]).expanduser()
    index = folder / "INDEX.md"
    if not index.is_file():
        print(f"missing-index: {index}")
        return 1
    lines = index.read_text().splitlines()
    problems = []

    if len(lines) > MAX_LINES:
        problems.append(f"index-too-long: {len(lines)} lines, max {MAX_LINES}; move detail into topics/")

    headings = [m.group(1).strip() for l in lines if (m := re.match(r"##\s+(.*)", l))]
    for name in SECTIONS:
        if not any(h.startswith(name) for h in headings):
            problems.append(f"missing-section: {name}")

    state, in_state = [], False
    for l in lines:
        if re.match(r"##\s+STATE", l):
            in_state = True
            continue
        if in_state and l.startswith("## "):
            break
        if in_state and l.strip():
            state.append(l)
    if len(state) > MAX_STATE_LINES:
        problems.append(f"state-too-long: {len(state)} lines, max {MAX_STATE_LINES}")
    if not any(l.startswith("- Updated:") for l in state):
        problems.append("state-no-date: STATE needs an '- Updated:' line")

    log = folder / "log.md"
    if not log.is_file():
        problems.append("missing-file: log.md")
    else:
        stamp = re.compile(r"(\d{4}-\d{2}-\d{2})(?: (\d{2}:\d{2}))?")
        updated = next((stamp.search(l) for l in state if l.startswith("- Updated:")), None)
        last = None
        for l in log.read_text().splitlines():
            m = stamp.search(l[:20])
            if m:
                last = m
        if updated and last:
            u = (updated.group(1), updated.group(2) or "00:00")
            g = (last.group(1), last.group(2) or "00:00")
            if g > u:
                problems.append(f"state-stale: STATE {' '.join(u)} is older than last log entry {' '.join(g)}")
    if not (folder / "topics").is_dir():
        problems.append("missing-dir: topics/")

    if problems:
        print("\n".join(problems))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
