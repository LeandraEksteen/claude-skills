#!/usr/bin/env python3
"""Lint one epic workspace folder so its spec, requirements, plan and test-plan files agree.

Usage: epic-lint.py <epic-dir> [--stage spec|plan|test-plan|all]

Reads only the folder; never the tracker or repos. Shared by /to-agent-spec, /build and /test-plan.
Exit 0 no ERROR (warnings allowed), 1 at least one ERROR, 2 bad invocation or no YAML parser.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

STAGES = {"spec", "plan", "test-plan", "all"}
CATEGORIES = {"functional", "edge-case", "business-rule", "data-contract", "operational", "out-of-scope"}
STATUSES = {"active", "blocked", "out-of-scope", "dropped"}
REQUIRED_KEYS = ["schema_version", "key", "origin", "jira_updated", "requirements"]
SOURCE_RE = re.compile(r"^(jira-ac|jira-comment|prd:|child:|slack:|gdoc:|artifact:|meeting:|user:)")
CASE_STATUSES = {"pending", "passed", "failed", "blocked", "dropped"}
CASE_FIELDS = ["Covers", "Preconditions", "Steps", "Expected", "Status"]
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
NOT_NAMES = {"passed", "pass", "failed", "fail", "ok", "on", "by"}
PLAN_FILES = ["plan.md", "pr-strategy.yaml", "checklist.md"]

TC_HEAD = re.compile(r"^###\s+(TC-(\d+))\s*(?:\[([^\]]*)\])?")
FIELD_LINE = re.compile(r"^([A-Z][A-Za-z -]*):\s?(.*)$")
SUPERSEDED_LINE = re.compile(r"^\s*[-*>|\s]*superseded\s*:\s*(.+)$", re.IGNORECASE)
QUOTED = re.compile(r'"([^"]+)"|`([^`]+)`|“([^”]+)”')


class Findings:
    def __init__(self):
        self.items = []

    def error(self, file, rule, detail):
        self.items.append(("ERROR", file, rule, detail))

    def warn(self, file, rule, detail):
        self.items.append(("WARN", file, rule, detail))


def load_yaml(path):
    """Return (data, error message or None). Exits 2 when no YAML parser is available."""
    try:
        import yaml  # noqa: PLC0415
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")), None
        except yaml.YAMLError as e:
            return None, str(e).splitlines()[0]
    except ImportError:
        pass
    if not shutil.which("ruby"):
        print("epic-lint needs PyYAML (`python3 -m pip install --user pyyaml`) or ruby on PATH.", file=sys.stderr)
        sys.exit(2)
    script = ("puts JSON.generate(YAML.safe_load(File.read(ARGV[0]), "
              "permitted_classes: [Time, Date]))")
    r = subprocess.run(["ruby", "-ryaml", "-rjson", "-rdate", "-e", script, str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        lines = (r.stderr or "unknown error").strip().splitlines()
        return None, lines[0] if lines else "unknown error"
    return json.loads(r.stdout), None


def section(text, name):
    """Lines of the '## <name>' section (case-insensitive), up to the next '## ' heading, or None."""
    lines = text.splitlines()
    head = re.compile(r"^##\s+" + re.escape(name) + r"\b", re.IGNORECASE)
    for i, line in enumerate(lines):
        if head.match(line):
            out = []
            for l in lines[i + 1:]:
                if l.startswith("## "):
                    break
                out.append(l)
            return out
    return None


def parse_table(lines):
    """Return (header cells, rows of cells) for the first markdown table in lines."""
    rows = []
    for l in lines:
        s = l.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(cells)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def ints(text):
    return [int(n) for n in re.findall(r"\d+", text)]


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


# 5.1 requirements.yaml

def check_requirements(d, f, ctx):
    path = d / "requirements.yaml"
    if not path.is_file():
        f.warn("requirements.yaml", "missing", "file not found")
        return None
    data, err = load_yaml(path)
    if err:
        f.error("requirements.yaml", "parse", f"cannot parse YAML: {err}")
        return None
    if not isinstance(data, dict):
        f.error("requirements.yaml", "schema", "top level must be a mapping")
        return None
    for k in REQUIRED_KEYS:
        if k not in data:
            f.error("requirements.yaml", "schema", f"missing top-level key '{k}'")
    key = data.get("key")
    if key is None:
        f.warn("requirements.yaml", "key-null", "key is null (fine only until a ticket exists)")
    elif d.name != str(key).lower():
        f.warn("requirements.yaml", "folder-name", f"folder '{d.name}' != lowercase key '{key}'")
    if data.get("jira_updated") is None:
        f.warn("requirements.yaml", "jira-updated-null", "jira_updated is null")
    if "superseded_terms" in data:
        terms = data["superseded_terms"]
        if isinstance(terms, list) and all(isinstance(t, str) and t.strip() for t in terms):
            ctx["terms"].extend(terms)
        else:
            f.warn("requirements.yaml", "superseded-terms",
                   "superseded_terms must be a list of non-empty strings; ignored")
    reqs = data.get("requirements")
    if not isinstance(reqs, list):
        f.error("requirements.yaml", "schema", "'requirements' must be a list")
        return {}
    by_id, seen_text, last = {}, {}, None
    for i, r in enumerate(reqs, 1):
        if not isinstance(r, dict):
            f.error("requirements.yaml", "schema", f"list item {i} is not a mapping")
            continue
        rid = r.get("id")
        if not is_int(rid):
            f.error("requirements.yaml", "id", f"list item {i} has non-integer id {rid!r}")
            label = f"item {i}"
        else:
            label = rid
            if rid in by_id:
                f.error("requirements.yaml", "id-unique", f"Req {rid} id repeated")
            elif last is not None and rid <= last:
                f.error("requirements.yaml", "id-order", f"Req {rid} is not greater than the previous id {last}")
            if rid not in by_id:
                by_id[rid] = r
            last = rid if last is None else max(last, rid)
        if r.get("category") not in CATEGORIES:
            f.error("requirements.yaml", "category",
                    f"Req {label} category {r.get('category')!r} not in {sorted(CATEGORIES)}")
        status = r.get("status")
        if status not in STATUSES:
            f.error("requirements.yaml", "status", f"Req {label} status {status!r} not in {sorted(STATUSES)}")
        for k in ("summary", "source", "source_text", "acceptance"):
            v = r.get(k)
            if v is None or (isinstance(v, str) and not v.strip()):
                f.error("requirements.yaml", "field", f"Req {label} missing '{k}'")
        acc = str(r.get("acceptance") or "").strip().lower()
        if status == "active" and acc.startswith("not yet checkable"):
            f.error("requirements.yaml", "acceptance", f"Req {label} is active but acceptance is 'Not yet checkable'")
        if status == "blocked" and not r.get("blocked_on"):
            f.error("requirements.yaml", "blocked-on", f"Req {label} is blocked but blocked_on is not set")
        text = " ".join(str(r.get("source_text") or "").split())
        if text:
            if text in seen_text:
                f.error("requirements.yaml", "source-text-dup",
                        f"Req {label} source_text is identical to Req {seen_text[text]}")
            else:
                seen_text[text] = label
        src = str(r.get("source") or "").strip().lstrip("'\"")
        if src and not SOURCE_RE.match(src):
            f.warn("requirements.yaml", "source-prefix",
                   f"Req {label} source '{src[:50]}' does not start with a known prefix (e.g. gdoc:<title>)")
    return by_id


# 5.2 spec.md

def check_spec(d, f, reqs, ctx):
    path = d / "spec.md"
    if not path.is_file():
        f.warn("spec.md", "missing", "file not found")
        return
    text = path.read_text(encoding="utf-8")
    ctx["terms"].extend(spec_terms(text))
    m = re.search(r"^Approved:\s*(yes|no)\b", text, re.MULTILINE | re.IGNORECASE)
    if not m:
        f.error("spec.md", "approved", "no 'Approved: yes|no' line")
    approved = bool(m and m.group(1).lower() == "yes")
    if reqs is None:
        if not (d / "requirements.yaml").exists():
            (f.error if approved else f.warn)("spec.md", "no-requirements",
                                              "spec.md exists but requirements.yaml is missing")
        return
    dec = section(text, "Decisions")
    if dec is None:
        f.error("spec.md", "decisions", "no '## Decisions' section")
    else:
        _, rows = parse_table(dec)
        counts = {}
        for row in rows:
            for i in set(ints(row[0] if row else "")):
                counts[i] = counts.get(i, 0) + 1
        for i in sorted(counts):
            if i not in reqs:
                f.error("spec.md", "decisions-unknown", f"Decisions row for Req {i}, which is not in requirements.yaml")
            elif counts[i] > 1:
                f.warn("spec.md", "decisions-dup", f"Req {i} has more than one Decisions row")
        for i in sorted(reqs):
            if i not in counts:
                f.error("spec.md", "decisions-missing", f"Req {i} has no Decisions row")
    oq = section(text, "Open questions") or []
    header, rows = parse_table(oq)
    col = next((n for n, h in enumerate(header) if "block" in h.lower()), len(header) - 1)
    blocks = set()
    for row in rows:
        if 0 <= col < len(row):
            blocks.update(ints(row[col]))
    for i in sorted(blocks):
        if reqs.get(i, {}).get("status") != "blocked":
            f.error("spec.md", "open-q-not-blocked", f"Open Questions blocks Req {i}, which is not a blocked requirement")
    for i, r in sorted(reqs.items()):
        if r.get("status") == "blocked" and i not in blocks:
            f.error("spec.md", "blocked-no-question", f"blocked Req {i} is not in the Open Questions table")


def spec_terms(text):
    terms = []
    for line in text.splitlines():
        m = SUPERSEDED_LINE.match(line)
        if m:
            terms += [next(g for g in q if g) for q in QUOTED.findall(m.group(1))]
    return terms


# 5.4 test-plan.md

def parse_cases(text):
    cases, cur, label = [], None, None
    for line in text.splitlines():
        m = TC_HEAD.match(line)
        if m:
            cur = {"id": m.group(1), "n": int(m.group(2)), "priority": (m.group(3) or "").strip().lower(),
                   "fields": {}}
            cases.append(cur)
            label = None
            continue
        if cur is None:
            continue
        if line.startswith("#"):
            cur, label = None, None
            continue
        fm = FIELD_LINE.match(line)
        if fm:
            label = fm.group(1).strip()
            cur["fields"][label] = fm.group(2)
        elif label:
            cur["fields"][label] += "\n" + line
    return cases


def case_status(c):
    words = c["fields"].get("Status", "").split()
    return words[0].lower().rstrip(".,;:") if words else ""


def check_test_plan(d, f, reqs, ctx):
    path = d / "test-plan.md"
    text = path.read_text(encoding="utf-8")
    cases = parse_cases(text)
    ctx["tc_ids"] = {c["id"] for c in cases}
    ctx["cases"] = cases
    if not cases:
        f.error("test-plan.md", "cases", "no '### TC-N' case headings found")
        return
    seen, last = set(), None
    for c in cases:
        if c["id"] in seen:
            f.error("test-plan.md", "tc-unique", f"{c['id']} repeated")
        elif last is not None and c["n"] < last:
            f.warn("test-plan.md", "tc-order", f"{c['id']} is lower than a previous case id")
        seen.add(c["id"])
        last = c["n"] if last is None else max(last, c["n"])
        for k in CASE_FIELDS:
            if k not in c["fields"]:
                f.error("test-plan.md", "case-field", f"{c['id']} missing '{k}:'")
        st = case_status(c)
        if "Status" in c["fields"] and st not in CASE_STATUSES:
            f.error("test-plan.md", "case-status", f"{c['id']} status '{st}' not in {sorted(CASE_STATUSES)}")
        if st in {"passed", "failed"}:
            res = c["fields"].get("Result", "")
            words = [w for w in re.findall(r"[A-Za-z][A-Za-z'.-]+", DATE_RE.sub(" ", res))
                     if w.lower() not in NOT_NAMES]
            if not (DATE_RE.search(res) and words):
                f.error("test-plan.md", "result", f"{c['id']} is {st} but Result lacks a name and a date (YYYY-MM-DD)")
    live = [c for c in cases if case_status(c) != "dropped"]
    if reqs is not None:
        covered = set()
        non_goal_cases = 0
        for c in live:
            cov = c["fields"].get("Covers", "")
            covered.update(int(n) for n in re.findall(r"#\s*(\d+)", cov))
            if "non-goal:" in cov.lower():
                non_goal_cases += 1
        not_tested = set()
        for l in section(text, "Not tested here") or []:
            for m in re.finditer(r"\bReqs?\s+#?\d+(?:\s*(?:,|and|&)\s*#?\d+)*", l):
                not_tested.update(ints(m.group(0)))
        for i, r in sorted(reqs.items()):
            if r.get("status") == "active" and i not in covered and i not in not_tested:
                f.error("test-plan.md", "uncovered", f"active Req {i} is covered by no case")
        # Non-goal cases cite the non-goal in words, not by id, so compare counts.
        oos = [i for i, r in reqs.items() if r.get("status") == "out-of-scope" and i not in not_tested and i not in covered]
        if len(oos) > non_goal_cases:
            f.warn("test-plan.md", "non-goal",
                   f"out-of-scope Req(s) {', '.join(map(str, sorted(oos)))} may have no 'non-goal:' case")
    m = re.search(r"^Summary:.*$", text, re.MULTILINE)
    if not m:
        f.warn("test-plan.md", "summary", "no 'Summary: N cases' line")
        return
    line = m.group(0)
    n = re.search(r"(\d+)\s+cases?\b", line)
    if n and int(n.group(1)) not in {len(cases), len(live)}:
        f.error("test-plan.md", "summary-count",
                f"Summary says {n.group(1)} cases, found {len(cases)} ({len(live)} not dropped)")
    h = re.search(r"(\d+)\s+high\b", line)
    if h:
        all_high = sum(1 for c in cases if c["priority"] == "high")
        live_high = sum(1 for c in live if c["priority"] == "high")
        if int(h.group(1)) not in {all_high, live_high}:
            f.error("test-plan.md", "summary-high",
                    f"Summary says {h.group(1)} high, found {all_high} ({live_high} not dropped)")


# 5.4 plan stage: pr-strategy.yaml, contract.md, plan.md

def expand_tc(text):
    ids = set()
    for a, b in re.findall(r"TC-(\d+)\s+to\s+TC-(\d+)", text):
        ids.update(f"TC-{n}" for n in range(int(a), int(b) + 1))
    ids.update(re.findall(r"TC-\d+", text))
    return ids


def check_plan(d, f, reqs, ctx):
    contract = d / "contract.md"
    if not contract.is_file():
        f.error("contract.md", "contract", "file not found")
    elif not re.search(r"^Approved:", contract.read_text(encoding="utf-8"), re.MULTILINE):
        f.error("contract.md", "contract", "no 'Approved:' line")
    path = d / "pr-strategy.yaml"
    ut_ids, mc_ids = set(), set()
    if not path.is_file():
        f.warn("pr-strategy.yaml", "missing", "file not found")
    else:
        data, err = load_yaml(path)
        if err:
            f.error("pr-strategy.yaml", "parse", f"cannot parse YAML: {err}")
            data = None
        prs = data.get("prs") if isinstance(data, dict) else None
        if data is not None and not isinstance(prs, list):
            f.error("pr-strategy.yaml", "schema", "needs a 'prs:' list")
        if isinstance(prs, list):
            ut_ids, mc_ids = check_prs(f, data, prs, reqs, ctx)
    plan = d / "plan.md"
    if plan.is_file():
        text = plan.read_text(encoding="utf-8")
        known = ut_ids | mc_ids | ctx.get("tc_ids", set())
        for l in text.splitlines():
            s = l.strip()
            if not s.startswith("|"):
                continue
            first = s.strip("|").split("|")[0]
            for tid in re.findall(r"\b(?:UT|MC|TC)-\d+\b", first):
                if tid not in known:
                    f.warn("plan.md", "matrix-id", f"test matrix names {tid}, which is not defined elsewhere")
        cases = ctx.get("cases")
        if cases is not None:
            live = [c for c in cases if case_status(c) != "dropped"]
            m = re.search(r"(\d+)\s+manual cases?", text)
            if m and int(m.group(1)) not in {len(cases), len(live)}:
                f.warn("plan.md", "count", f"plan says {m.group(1)} manual cases, test-plan.md has {len(cases)}")
            m = re.search(r"(\d+)\s+high-priority", text)
            highs = {sum(1 for c in cases if c["priority"] == "high"), sum(1 for c in live if c["priority"] == "high")}
            if m and int(m.group(1)) not in highs:
                f.warn("plan.md", "count", f"plan says {m.group(1)} high-priority, test-plan.md has {max(highs)}")


def check_prs(f, data, prs, reqs, ctx):
    F = "pr-strategy.yaml"
    ids = [p.get("id") for p in prs if isinstance(p, dict)]
    seen, ut_ids, mc_ids, in_prs = set(), set(), set(), set()
    for pid in ids:
        if pid in seen:
            f.error(F, "pr-unique", f"PR {pid} id repeated")
        seen.add(pid)
    for p in prs:
        if not isinstance(p, dict):
            f.error(F, "schema", "a 'prs' item is not a mapping")
            continue
        pid = p.get("id")
        deps = p.get("depends_on") or []
        base = str(p.get("base") or "")
        if base.startswith("pr:"):
            try:
                n = int(base[3:])
            except ValueError:
                n = None
            if n not in seen:
                f.error(F, "pr-base", f"PR {pid} base '{base}' names no existing PR")
            elif n not in deps:
                f.error(F, "pr-base-dep", f"PR {pid} stacks on PR {n} but {n} is not in depends_on")
        for rid in p.get("requirements") or []:
            in_prs.add(rid)
            if reqs is None:
                continue
            if rid not in reqs:
                f.error(F, "pr-req-unknown", f"PR {pid} cites Req {rid}, which is not in requirements.yaml")
            elif reqs[rid].get("status") in {"out-of-scope", "blocked", "dropped"}:
                f.error(F, "pr-req-status", f"PR {pid} cites Req {rid}, which is {reqs[rid].get('status')}")
        for t in p.get("tests") or []:
            m = re.match(r"^([A-Z]+)-(\d+)\b", str(t).strip())
            if not m:
                f.error(F, "test-id", f"PR {pid} test '{str(t)[:40]}' does not start with an id like UT-3")
            elif m.group(1) == "TC":
                f.error(F, "test-tc", f"PR {pid} uses {m.group(0)} in tests; TC- ids belong to test-plan.md")
            elif m.group(1) == "UT":
                if m.group(0) in ut_ids:
                    f.error(F, "ut-unique", f"{m.group(0)} used by more than one test")
                ut_ids.add(m.group(0))
    if reqs is not None:
        for i, r in sorted(reqs.items()):
            if r.get("status") == "active" and i not in in_prs:
                f.error(F, "orphan", f"active Req {i} is in no PR")
    order = data.get("merge_order") or []
    if sorted(map(str, order)) != sorted(map(str, seen)) or len(order) != len(seen):
        f.error(F, "merge-order", f"merge_order {order} is not exactly the PR ids {sorted(seen, key=str)}")
    tc_known = ctx.get("tc_ids", set())
    for entry in data.get("manual_checks") or []:
        s = str(entry)
        mc_ids.update(re.findall(r"\bMC-\d+\b", s))
        for tid in sorted(expand_tc(s)):
            if tid not in tc_known:
                f.error(F, "manual-tc", f"manual_checks cites {tid}, which is not in test-plan.md")
    return ut_ids, mc_ids


# 5.3 stale references

def check_stale(d, f, ctx, stage_spec, stage_plan):
    terms = sorted({t.strip().lower() for t in ctx["terms"] if len(t.strip()) >= 3})
    if not terms:
        return
    files = []
    if stage_spec:
        files.append("spec.md")
    if stage_plan:
        files += PLAN_FILES + sorted(p.name for p in d.glob("pr-*.md"))
    for name in files:
        path = d / name
        if not path.is_file():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if name == "spec.md" and SUPERSEDED_LINE.match(line):
                continue
            low = line.lower()
            for t in terms:
                if t in low:
                    f.warn(name, "stale-ref", f"line {n} still uses superseded term '{t}'")


def main(argv):
    args = argv[1:]
    stage = "all"
    if "--stage" in args:
        i = args.index("--stage")
        if i + 1 >= len(args) or args[i + 1] not in STAGES:
            print(__doc__, file=sys.stderr)
            return 2
        stage = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    d = Path(args[0]).expanduser().resolve()
    if not d.is_dir():
        print(f"epic-lint: {d} is not a directory", file=sys.stderr)
        return 2

    def want(s):
        return stage in (s, "all")

    out, ctx = Findings(), {"terms": []}
    f = Findings()
    reqs = check_requirements(d, f, ctx)
    out.items += f.items if want("spec") else [x for x in f.items if x[2] == "parse"]
    if want("spec"):
        check_spec(d, out, reqs, ctx)
    elif (d / "spec.md").is_file():
        ctx["terms"].extend(spec_terms((d / "spec.md").read_text(encoding="utf-8")))
    if (d / "test-plan.md").is_file():
        f = Findings()
        check_test_plan(d, f, reqs, ctx)
        if want("test-plan"):
            out.items += f.items
    if want("plan"):
        check_plan(d, out, reqs, ctx)
    check_stale(d, out, ctx, want("spec"), want("plan"))

    for level, file, rule, detail in out.items:
        print(f"{level} {file} {rule} {detail}")
    errors = sum(1 for x in out.items if x[0] == "ERROR")
    warns = len(out.items) - errors
    print(f"epic-lint {d.name} (stage {stage}): {errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
