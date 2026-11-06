#!/usr/bin/env python3
"""Export a test-plan.md checklist to a CSV (for the Sheet) or HTML (for the Doc), and import results back.

  checklist-sheet.py export <test-plan.md> [out.csv]
  checklist-sheet.py html <test-plan.md> [out.html]
  checklist-sheet.py import <filled.csv> <test-plan.md>
"""
import csv
import html as H
import re
import sys
from pathlib import Path

HEAD = re.compile(r"^### (TC-\d+) \[(high|normal)\] (.*)$")
LABELS = ["Covers", "Story", "Preconditions", "Steps", "Expected", "Also check",
          "Unit-tested", "Status", "Result", "History"]
LABEL = re.compile(r"^(" + "|".join(re.escape(l) for l in LABELS) + r"):\s?(.*)$")
STATUSES = {"pending", "passed", "failed", "blocked", "dropped"}
SHEET_COLS = ["Case", "Priority", "Title", "Story", "Covers", "Preconditions", "Steps", "Expected",
              "Also check", "Unit-tested", "Status", "Tested by", "Date", "Notes"]


def parse(text):
    """Return (lines, cases). cases: id -> {"start","end","priority","title","fields"{label:[lines]}}."""
    lines = text.split("\n")
    cases, cur, label = {}, None, None
    for i, line in enumerate(lines):
        m = HEAD.match(line)
        if m:
            if cur:
                cur["end"] = i
            cur = {"start": i, "end": len(lines), "priority": m.group(2), "title": m.group(3), "fields": {}}
            cases[m.group(1)] = cur
            label = None
            continue
        if cur is None:
            continue
        if line.startswith("## "):
            cur["end"] = i
            cur = None
            continue
        lm = LABEL.match(line)
        if lm:
            label = lm.group(1)
            cur["fields"][label] = [lm.group(2)] if lm.group(2) else []
        elif label:
            cur["fields"][label].append(line)
    return lines, cases


def field(case, name):
    return "\n".join(case["fields"].get(name, [])).strip()


def export(plan, out):
    _, cases = parse(Path(plan).read_text())
    if not cases:
        sys.exit("No cases found: expected '### TC-N [high|normal] title' headings.")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(SHEET_COLS)
        for cid, c in cases.items():
            w.writerow([cid, c["priority"], c["title"], field(c, "Story"), field(c, "Covers"),
                        field(c, "Preconditions"), field(c, "Steps"), field(c, "Expected"),
                        field(c, "Also check"), field(c, "Unit-tested"),
                        field(c, "Status") or "pending", "", "", field(c, "Result")])
    print(f"Wrote {len(cases)} cases to {out}")


def esc(t):
    return H.escape(t, quote=False)


def case_html(cid, c):
    out = [f"<h3>{esc(cid)} [{c['priority']}] {esc(c['title'])}</h3>"]
    for name in ["Covers", "Story", "Preconditions", "Steps", "Expected", "Also check", "Unit-tested"]:
        val = field(c, name)
        if not val:
            continue
        body = "<br>".join(esc(l) for l in val.split("\n") if l.strip())
        out.append(f"<p><b>{name}:</b> {body}</p>")
    out.append(f"<p><b>Status:</b> {esc(field(c, 'Status') or 'pending')}</p>")
    if field(c, "Result"):
        out.append(f"<p><b>Result:</b> {esc(field(c, 'Result'))}</p>")
    return "\n".join(out)


def table_html(rows):
    cells = [[esc(x.strip()) for x in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for i, r in enumerate(cells) if i != 1]  # drop the markdown separator row
    out = ["<table border='1' cellpadding='4'>"]
    for r in cells:
        out.append("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>")
    return "\n".join(out + ["</table>"])


def to_html(plan, out):
    lines, cases = parse(Path(plan).read_text())
    if not cases:
        sys.exit("No cases found: expected '### TC-N [high|normal] title' headings.")
    first = next(i for i, l in enumerate(lines) if HEAD.match(l))
    parts, header = ["<html><body>"], []
    for l in lines[:first]:
        if l.startswith("# "):
            parts.append(f"<h1>{esc(l[2:])}</h1>")
        elif l.startswith("## "):
            continue  # the Cases heading is added once below
        elif l.strip():
            header.append(l)
    for l in header:
        m = re.match(r"^([A-Za-z][A-Za-z ]*):\s?(.*)$", l)
        if m:
            parts.append(f"<p><b>{esc(m.group(1))}:</b> {esc(m.group(2))}</p>")
        elif l.startswith("- "):
            parts.append(f"<p>&bull; {esc(l[2:])}</p>")
        else:
            parts.append(f"<p>{esc(l)}</p>")
    parts.append("<h2>Cases</h2>")
    parts += [case_html(cid, c) for cid, c in cases.items()]
    in_oq, rows = False, []
    for l in lines[first:]:
        if re.match(r"^## open questions", l, re.I):
            in_oq = True
        elif l.startswith("## "):
            in_oq = False
        elif in_oq and l.startswith("|"):
            rows.append(l)
    if rows:
        parts += ["<h2>Open questions</h2>", table_html(rows)]
    parts.append("</body></html>")
    Path(out).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {out}")


def set_field(lines, case, name, value):
    """Rewrite one single-line field of a case in place; add it after Status if missing."""
    for i in range(case["start"], case["end"]):
        if lines[i].startswith(name + ":"):
            lines[i] = f"{name}: {value}".rstrip()
            return
    for i in range(case["start"], case["end"]):
        if lines[i].startswith("Status:"):
            lines.insert(i + 1, f"{name}: {value}".rstrip())
            return


def do_import(sheet, plan):
    path = Path(plan)
    lines, cases = parse(path.read_text())
    rows = list(csv.DictReader(open(sheet, newline="", encoding="utf-8-sig")))
    problems, applied = [], 0
    # Apply bottom-up so inserted lines do not shift cases not yet processed.
    for row in sorted(rows, key=lambda r: -(cases.get(r["Case"].strip(), {"start": -1})["start"])):
        cid = row["Case"].strip()
        status = row["Status"].strip().lower()
        who, date, notes = row["Tested by"].strip(), row["Date"].strip(), row["Notes"].strip()
        if cid not in cases:
            problems.append(f"{cid}: not in {path.name}, skipped")
            continue
        if status not in STATUSES:
            problems.append(f"{cid}: status '{row['Status']}' is not one of {sorted(STATUSES)}, skipped")
            continue
        case = cases[cid]
        old_status = field(case, "Status") or "pending"
        if status == old_status and not who:
            continue  # untouched row
        if status in {"passed", "failed"} and not who:
            problems.append(f"{cid}: {status} needs a name in 'Tested by', skipped")
            continue
        old_result = field(case, "Result")
        who_date = ", ".join(x for x in (who, date) if x)
        result = ". ".join(x for x in (who_date, notes) if x)
        if old_result and old_result != result:
            set_field(lines, case, "History",
                      (field(case, "History") + " | " if field(case, "History") else "")
                      + f"{old_status}: {old_result}")
        set_field(lines, case, "Result", result)
        set_field(lines, case, "Status", status)
        applied += 1
    path.write_text("\n".join(lines))
    print(f"Applied {applied} result(s) to {path}")
    for p in problems:
        print("  !", p)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "export":
        export(a[1], a[2] if len(a) > 2 else str(Path(a[1]).with_suffix(".csv")))
    elif len(a) >= 2 and a[0] == "html":
        to_html(a[1], a[2] if len(a) > 2 else str(Path(a[1]).with_suffix(".html")))
    elif len(a) == 3 and a[0] == "import":
        do_import(a[1], a[2])
    else:
        sys.exit(__doc__)
