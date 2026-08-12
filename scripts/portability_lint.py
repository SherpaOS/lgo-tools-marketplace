#!/usr/bin/env python3
"""Portability lint — executable enforcement of ship-check Step 2.

WHY THIS EXISTS
---------------
`ship-check` Step 2 has defined a portability gate for months. It is Markdown read
by an agent, so it fires only when someone remembers to read it. Three independent
reviews reached the same conclusion within one day (2026-08-08/09):

  panel (Gemini):  "An LLM reading Markdown instructions is not a gate; it is a
                    suggestion."
  panel (GPT-5.2): "If you won't add CI, then you don't have a gate - just
                    stronger prose."
  Gem (mission 005 Gate 1, Finding 4): "There is no automated portability gate...
                    add a linter that fails, making QA a verification gate rather
                    than the only gate."

Proof the concern is real: on 2026-08-09 a QA agent audited a deliverable
containing three hardcoded tenant ids and cited two of them as EVIDENCE THAT THE
ACCEPTANCE CRITERIA PASSED. The rule existed. Nothing executed it.

This implements the mechanically decidable BLOCK checks from ship-check Step 2:
  1 owner identity tokens · 2 absolute local paths · 3 opaque tenant ids
  5 unresolved author notes
Checks 4 (named private stores) and 6 (claim-vs-content contradiction) need
judgement and are deliberately NOT attempted here - the agent still owns those.

OPERATOR-AGNOSTIC BY CONSTRUCTION
---------------------------------
ship-check 2a: "This gate must itself be operator-agnostic, or it reproduces the
bug it exists to catch." No owner name appears in this file. Identity tokens are
DATA, read from --tokens (default: portability-tokens.json). No tokens file means
check 1 is SKIPPED and says so - it never silently passes.
"""
from __future__ import annotations
import argparse, json, os, re, sys, fnmatch

# ── what reaches a customer (ship-check 2b) ────────────────────────────────
INCLUDE = ["plugins/*/skills/**/*", "plugins/*/*.md", "plugins/*/references/**/*",
           "plugins/*/.claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]
EXCLUDE_DIRS = {".git", ".github", "config", "infra", "scripts", "node_modules", "dist"}
# the gate quotes the patterns it searches for and will always match itself
EXCLUDE_PATH_PARTS = ["skills/ship-check/"]
EXCLUDE_ROOT_FILES = {"CHANGELOG.md", "README.md", "RELEASING.md",
                      "portability-allowlist.md", "surface-matrix.md"}

CHECKS = {
    2: ("absolute local paths",
        re.compile(r"(?:/Users/[A-Za-z0-9._-]+|/home/[a-z][A-Za-z0-9._-]*|C:\\+Users\\+[A-Za-z0-9._-]+)")),
    3: ("opaque tenant ids",
        re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
                   r"|\b[0-9a-f]{32}\b"
                   r"|collection://[0-9a-f-]{16,}")),
    5: ("unresolved author notes",
        re.compile(r"\[DECISION:|\bTODO:|\bFIXME\b|\bHACK:|NOTE TO SELF")),
}
# placeholders that are the POINT, not a leak (ship-check allows these explicitly)
PLACEHOLDER = re.compile(r"<[A-Za-z_ -]+>|\$\{[A-Za-z_]+\}|EXAMPLE|xxxx|0{8}|your-|<your")

def in_scope(path: str) -> bool:
    parts = path.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return False
    if any(x in path.replace(os.sep, "/") for x in EXCLUDE_PATH_PARTS):
        return False
    if os.sep not in path and path in EXCLUDE_ROOT_FILES:
        return False
    rel = path.replace(os.sep, "/")
    return any(fnmatch.fnmatch(rel, pat) for pat in INCLUDE)

def load_allowlist(path: str) -> list[tuple[str, set[str]]]:
    """Parse the allowlist as (file-or-glob, {strings}) PAIRS.

    A suppression must match BOTH the file and the string. Extracting bare tokens
    globally is a real bug I shipped and caught on 2026-08-09: `Jamie` and `TODO:`
    appear as backticked strings in rows scoped to specific files, and treating them
    as global tokens silently disabled checks 1 and 5 across the WHOLE repo. An
    allowlist that turns a check off everywhere is worse than no allowlist.
    """
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path):
        if not line.lstrip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 2:
            continue
        files = re.findall(r"`([^`]+)`", cols[0])
        strings = set(re.findall(r"`([^`]+)`", cols[1]))
        if not files or not strings:
            continue
        for f in files:
            rows.append((f, strings))
    return rows

def main() -> int:
    ap = argparse.ArgumentParser(description="Fail the build on portability leaks in shipped content.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--tokens", default="portability-tokens.json",
                    help="JSON: {\"identity\": [\"name\", \"entity\", \"domain\", ...]}")
    ap.add_argument("--allowlist", default="portability-allowlist.md")
    ap.add_argument("--warn-only", action="store_true", help="report without failing (local use only)")
    ap.add_argument("--canary", default="learning-on-the-go",
                    help="a path fragment the scan MUST hit; proves the scanner is alive")
    a = ap.parse_args()
    os.chdir(a.root)

    identity, public = [], []
    if os.path.exists(a.tokens):
        _tok = json.load(open(a.tokens))
        identity = [t for t in _tok.get("identity", []) if t]
        public = [t for t in _tok.get("public_contact", []) if t]
    allow = load_allowlist(a.allowlist)

    checks = dict(CHECKS)
    if identity:
        checks[1] = ("owner identity tokens",
                     re.compile("|".join(re.escape(t) for t in identity), re.I))

    files = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            p = os.path.relpath(os.path.join(dirpath, fn), ".")
            if in_scope(p):
                files.append(p)

    findings, suppressed, canary_hit = [], [], False
    for p in sorted(files):
        try:
            text = open(p, errors="ignore").read()
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for num, (label, rx) in sorted(checks.items()):
                for m in rx.finditer(line):
                    hit = m.group(0)
                    if PLACEHOLDER.search(hit):
                        continue
                    # ship-check 2a: the plugin's PUBLIC support address is fine.
                    # Without this the correct address trips the entity token inside it.
                    if any(c in line and hit.lower() in c.lower() for c in public):
                        continue
                    rec = (num, label, p, lineno, hit, line.strip()[:110])
                    rel = p.replace(os.sep, "/")
                    # BOTH must match: the file (or glob) AND the string
                    ok = False
                    for pat, strings in allow:
                        if not (fnmatch.fnmatch(rel, pat)
                                or fnmatch.fnmatch(rel, pat.rstrip("/") + "/*")
                                or rel == pat):
                            continue
                        # `*` in the String column = blanket exemption for this file.
                        # Deliberately explicit: a whole-file pass must LOOK like one.
                        if "*" in strings or any(hit == t or hit in t or t in line for t in strings):
                            ok = True
                            break
                    if ok:
                        suppressed.append(rec)
                    else:
                        findings.append(rec)
                    if a.canary and a.canary in p:
                        canary_hit = True   # found it, blocked or baselined — scanner is alive

    out = ["## Portability lint", "",
           f"- scanned: **{len(files)}** shipped files",
           f"- checks run: {', '.join(f'{n} ({l})' for n, (l, _) in sorted(checks.items()))}",
           f"- identity tokens: **{len(identity)}**" if identity else
           "- ⚠️ **check 1 SKIPPED — no tokens file.** Owner-identity leaks are NOT being checked.",
           ""]
    if findings:
        out += [f"### 🔴 {len(findings)} finding(s) — BLOCK", ""]
        for num, label, p, ln, hit, ctx in findings:
            out += [f"- **check {num} ({label})** `{p}:{ln}` → `{hit}`", f"  <br>`{ctx}`"]
        out += [""]
    if suppressed:
        out += [f"### allowlisted ({len(suppressed)}) — re-listed so they stay visible", ""]
        out += [f"- check {n} `{p}:{ln}` → `{h}`" for n, _, p, ln, h, _ in suppressed] + [""]
    if not files:
        out += ["### 🔴 SCANNED NOTHING — this is a FAILURE, not a pass", "",
                "A gate that examines zero files and reports clean is worse than no gate: it "
                "produces a green check that means nothing. Check `--root` — it must point at "
                "the repository root, not at a single plugin or skill directory.", ""]
    elif not findings and not suppressed:
        out += ["✅ clean", ""]
    out += ["*Checks 4 (named private stores) and 6 (claim-vs-content contradiction) "
            "require judgement and are NOT attempted here — the agent still owns those.*"]

    report = "\n".join(out)
    print(report)
    if (sp := os.environ.get("GITHUB_STEP_SUMMARY")):
        open(sp, "a").write(report + "\n")

    # ── integrity failures — these are NOT policy findings and --warn-only does not
    # excuse them. A leak is a thing the gate found; these mean the gate cannot be
    # trusted to have looked at all, which is the failure that silently ships.
    if not files:
        print("\n::error::Portability lint scanned 0 files — refusing to report a pass. "
              "--root must be the repository root.")
        return 1

    # A scanner that finds nothing is usually broken, not lucky. This used to warn only
    # when findings already existed — exactly backwards: the canary matters MOST when
    # the scan came back empty, which is the case it could not report on.
    if a.canary and not canary_hit:
        print(f"\n::error::canary '{a.canary}' produced no hit — the scanner is not "
              "looking where you think it is.")
        return 1

    if findings and not a.warn_only:
        print(f"\n::error::Portability lint FAILED — {len(findings)} leak(s) in shipped content.")
        return 1
    if findings:
        print("\nWARN-ONLY: would have failed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
