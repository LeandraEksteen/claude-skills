#!/usr/bin/env python3
"""Validate skills in ./skills against the skill-authoring rules. Exit 0 ok, 1 violations, 2 IO error."""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED = re.compile(r"^(claude|anthropic)([-_]|$)", re.IGNORECASE)
MAX_DESC, MAX_WORDS = 1024, 5000
XML_EXEMPT = {"argument-hint"}

def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block, body = text[4:end], text[end + 4:].lstrip("\n")
    fields = {}
    for line in block.splitlines():
        if not line or line[0] in " \t#-" or ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        fields[k.strip()] = v
    return fields, body

def check(skill_dir):
    out, folder = [], skill_dir.name
    entries = {p.name for p in skill_dir.iterdir()}
    if not KEBAB.match(folder): out.append(("folder-naming", folder))
    if RESERVED.match(folder): out.append(("reserved-prefix", folder))
    if any(e.lower() == "readme.md" for e in entries): out.append(("no-readme", folder))
    if "SKILL.md" not in entries:
        wrong = [e for e in entries if e.lower() == "skill.md"]
        out.append(("skill-md-wrong-case" if wrong else "missing-skill-md", folder))
        return out
    parsed = parse_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    if parsed is None:
        out.append(("frontmatter-missing", folder)); return out
    fields, body = parsed
    name = fields.get("name")
    if not name: out.append(("name-missing", folder))
    else:
        if not KEBAB.match(name): out.append(("name-format", name))
        if name != folder: out.append(("name-folder-mismatch", f"{name} != {folder}"))
        if RESERVED.match(name): out.append(("reserved-prefix", name))
    desc = fields.get("description")
    if not desc: out.append(("description-missing", folder))
    elif len(desc) > MAX_DESC: out.append(("description-too-long", f"{len(desc)} chars"))
    for k, v in fields.items():
        if k not in XML_EXEMPT and ("<" in v or ">" in v):
            out.append(("frontmatter-xml", k))
    if len(body.split()) > MAX_WORDS: out.append(("skill-md-too-long", f"{len(body.split())} words"))
    return out

def main(argv):
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: {SKILLS_DIR} does not exist", file=sys.stderr); return 2
    names = set(argv[1:])
    dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if names:
        dirs = [d for d in dirs if d.name in names]
        for n in names - {d.name for d in dirs}:
            print(f"WARN: skill '{n}' not found", file=sys.stderr)
    bad = [(d.name, r, detail) for d in dirs for r, detail in check(d)]
    if bad:
        print(f"FAIL: {len(bad)} violation(s) across {len(dirs)} skill(s):\n")
        for skill, rule, detail in sorted(bad, key=lambda b: b[1]):
            print(f"  [{rule}] {skill}: {detail}")
        return 1
    print(f"OK: {len(dirs)} skill(s) checked, 0 violations.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
