#!/usr/bin/env python3
"""Re-derive every checkable claim on the nitrosend-first-send ROOT landing page.

WHY (shift 640/641). GitHub renders a repo's landing page from a README in the repo ROOT (or
`.github/`, or `docs/`). This repo published only `products/nitrosend-first-send/README.md`, so
`bin/repo_landing_audit.py` measured it BLANK: GitHub's own resolver found no README at all and a
stranger saw a bare file tree. The fix adds a ROOT page via a `src => dest` allowlist line and
moves nothing, because raw/blob URLs under the nested prefix have already been handed to third
parties. The landing page is then the repo's only ungated public surface, and this script is what
keeps it true.

THE PAGE IS IDENTIFIED BY ITS MARKER, NOT BY ITS PATH (shift 640's lesson). It lives at the repo
root once published and at `products/nitrosend-first-send/GITHUB_ROOT_README.md` in our tree. Comparing a
path would compare the wrong file, so this script locates the page by the HTML-comment marker
`<!-- qf-landing-page: nitrosend-first-send -->` and refuses anything that does not carry exactly
one.

  python3 products/nitrosend-first-send/verify_root_readme.py            # our tree
  python3 .../verify_root_readme.py --page README.md --repo-root .        # a fresh clone
exit 0 = every claim re-derived; 1 = at least one FAIL.
"""
import argparse, re, sys
from pathlib import Path

MARKER = "<!-- qf-landing-page: nitrosend-first-send -->"
HERE = Path(__file__).resolve().parent

# claim on the page -> (note that must declare it, the note's OWN declaration of it)
#
# The third element is the note's DECLARATION, not a bare version substring. The first draft
# checked `"0.11.6" in report_sdk.md`, and the tamper harness showed that leg green after the
# note's Versions line was changed to 0.11.9 -- because the install command one line below still
# said `@nitrosend/sdk@0.11.6`. A version that appears anywhere in a long note is not the version
# the note declares, so the anchor has to be the declaring line.
VERSION_CLAIMS = [
    ("`@nitrosend/cli` 0.3.8", "report_cli.md", "`@nitrosend/cli` **0.3.8**"),
    ("`@nitrosend/sdk` 0.11.6", "report_sdk.md", "`@nitrosend/sdk` **0.11.6**"),
    ("NitroMTA 0.1.6", "report_nitromta.md", "`nitromta --version` → **`nitromta 0.1.6`**"),
]
NOTES = ["report_cli.md", "report_sdk.md", "report_mcp.md", "report_nitromta.md"]
DIR = "products/nitrosend-first-send"

# The four transcripts report_mcp.md cites that are NOT in this repository. The nested index says
# so ("the MCP note names four Codex transcripts that do not" ship); the first draft of the
# landing page claimed instead that "each note ships the scripts and raw command output it cites",
# which is false and was a STRENGTHENING of the nested text -- caught by the Opus critic. These
# legs exist so that claim cannot come back.
CODEX_TRANSCRIPTS = ["codex_run_20261025T171105Z.txt", "codex_run_20261025T171233Z.txt",
                     "codex_control_20261025T172256Z.txt", "mcp_run_20261025T170934Z.txt"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default=str(HERE / "GITHUB_ROOT_README.md"),
                    help="the landing page to check (root README.md in a published clone)")
    ap.add_argument("--repo-root", default=str(HERE.parents[1]),
                    help="the tree the page's links are relative to")
    a = ap.parse_args()
    page, root = Path(a.page), Path(a.repo_root)
    ok = fails = 0

    def check(cond, what):
        nonlocal ok, fails
        if cond:
            ok += 1
            print(f"  ok    {what}")
        else:
            fails += 1
            print(f"  FAIL  {what}")

    if not page.exists():
        print(f"FAIL  landing page not found at {page}")
        return 1
    txt = page.read_text()

    check(txt.count(MARKER) == 1, f"the page carries exactly 1 marker (found {txt.count(MARKER)})")

    # 1. Every relative link on the page must resolve inside the tree the page sits in. This is
    #    the claim the move actually threatens: the nested README's links are relative to the
    #    nested directory and would ALL break if that text were reused verbatim at the root.
    links = re.findall(r"\]\(([^)]+)\)", txt)
    rel = [l for l in links if not l.startswith(("http://", "https://", "#", "mailto:"))]
    check(len(rel) == 16, f"the page links exactly 16 files in the repo (found {len(rel)})")
    broken = [l for l in rel if not (root / l).exists()]
    check(not broken, f"all {len(rel)} relative link(s) resolve under {root} "
                      + (f"-- BROKEN: {broken}" if broken else ""))

    # 2. Every version number the page attributes to a note must be in that note. A version is
    #    the single most copy-pasteable thing on the page and the easiest to let go stale.
    for claim, fname, decl in VERSION_CLAIMS:
        src = HERE / fname
        check(claim in txt, f"the page states {claim}")
        check(src.exists() and decl in src.read_text(),
              f"{fname} declares the version the page attributes to it ({decl})")

    # 3. The headline count must equal the number of notes the page actually links.
    linked_notes = [n for n in NOTES if f"{DIR}/{n}" in rel]   # exact path, not endswith: a
    check(len(linked_notes) == 4, f"all 4 field notes are linked (found {len(linked_notes)})")
    check("Four dated field notes" in txt, "the headline says 'Four dated field notes'")

    # 4. The page's stated line count for send.ts, read OFF THE PAGE and compared with the file.
    #    The first draft of this check measured the file and compared it with the constant 30 --
    #    which validated the file, not the page, and the tamper harness caught it by editing the
    #    page to "31-line" with the leg still green. Parse the number the page emits.
    send = HERE / "send.ts"
    n = len(send.read_text().splitlines()) if send.exists() else -1
    m = re.search(r"the (\d+)-line SDK script", txt)
    check(m is not None, "the page states a line count for send.ts")
    check(m is not None and int(m.group(1)) == n,
          f"the page's send.ts line count ({m.group(1) if m else '?'}) equals the file's ({n})")

    # 5. THE SHIPPING GAP. For each transcript report_mcp.md cites: it must really be cited, and
    #    it must really be absent from the repo -- and then the page must SAY four of them are
    #    absent. A page that claims everything ships is the failure this block prevents.
    mcp = (HERE / "report_mcp.md").read_text() if (HERE / "report_mcp.md").exists() else ""
    cited = [n for n in CODEX_TRANSCRIPTS if n in mcp]
    absent = [n for n in CODEX_TRANSCRIPTS if not (HERE / n).exists()]
    check(len(cited) == 4, f"report_mcp.md cites all 4 Codex transcripts (found {len(cited)})")
    check(len(absent) == 4, f"all 4 of those transcripts are absent from the repo (found {len(absent)})")
    check("four Codex transcripts that are **not** in this repository" in txt,
          "the page states that four cited Codex transcripts do not ship")
    #    The CLI note cites no shipped artifact at all, so the page must not imply one.
    cli = (HERE / "report_cli.md").read_text() if (HERE / "report_cli.md").exists() else ""
    cli_artifacts = [f.name for f in HERE.iterdir() if f.is_file() and f.name in cli]
    check(not cli_artifacts,
          f"report_cli.md cites no file that ships beside it (found {cli_artifacts})")
    check("quotes its payloads inline and ships no separate\nartifact" in txt
          or "quotes its payloads inline and ships no separate artifact" in txt,
          "the page states the CLI note ships no separate artifact")

    # 6. DISCLOSURE AND THE AUTONOMY CAVEAT. Both are claims a stranger weighs the rest of the
    #    page against, and deleting either left the first draft of this verifier 18/18 green.
    for needle, what in (
            ("AI-run studio", "the page discloses that Quietforge Studio is an AI-run studio"),
            ("no human in the authoring loop", "the page discloses no human in the authoring loop"),
            ("did not exercise signup or sender\ncreation", None),
            ("--approve-for-me", "the page names the flag the first send needed")):
        if what is None:
            check(needle in txt or needle.replace("\n", " ") in txt,
                  "the page carries the MCP note's signup/sender-creation caveat")
        else:
            check(needle in txt, what)
    check("did not exercise signup or sender creation" in mcp.replace("\n", " "),
          "report_mcp.md really makes the signup/sender-creation caveat the page repeats")

    # 7. The two credential claims the page makes about its own scripts. The anchor is the READ
    #    EXPRESSION, not the bare variable name: both scripts also mention NITROSEND_API_KEY in
    #    their error strings, so `"NITROSEND_API_KEY" in body` stayed true after the tamper
    #    harness rewrote the actual read -- a leg that cannot fail for the reason it names.
    for fname, read_expr in (("send.ts", 'process.env.NITROSEND_API_KEY'),
                             ("probe_mcp.py", 'os.environ.get("NITROSEND_API_KEY")')):
        body = (HERE / fname).read_text() if (HERE / fname).exists() else ""
        check(read_expr in body,
              f"{fname} reads its key from the environment as {read_expr}, as the page says")

    # 8. The page itself must carry no credential-shaped literal. `secret_scan.py` is the real
    #    control; this is a cheap second look at the one file a stranger reads first.
    bad = re.findall(r"(?i)\b(?:sk|pk|ns)[-_][A-Za-z0-9]{16,}\b|\b[0-9a-f]{64}\b", txt)
    check(not bad, f"the page carries no key-shaped or 64-hex literal (found {bad[:3]})")

    print(f"{ok} ok, {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
