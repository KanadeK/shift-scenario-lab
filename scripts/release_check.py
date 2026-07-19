from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> str:
    return subprocess.check_output(command, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def main() -> None:
    if run(["git", "status", "--porcelain"]).strip():
        raise SystemExit("working tree is not clean")
    if "## 0.1.0" not in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"):
        raise SystemExit("CHANGELOG lacks 0.1.0")
    if not list((ROOT / "dist").glob("shift_scenario_lab-0.1.0*")):
        raise SystemExit("build artifacts are missing")
    source = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("*.py"))
    unfinished_markers = ("TO" + "DO", "FI" + "XME", "Not" + "Implemented", "place" + "holder")
    if re.search("|".join(unfinished_markers), source, re.I):
        raise SystemExit("source contains an unfinished marker")
    if re.search(r"(gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})", source):
        raise SystemExit("possible secret found")
    authors = run(["git", "log", "--format=%an <%ae>"]).splitlines()
    if len(set(authors)) != 1:
        raise SystemExit("unexpected commit author found")
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True)
    print("release-check passed")


if __name__ == "__main__":
    main()
