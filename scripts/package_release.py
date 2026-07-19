from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASE = ROOT / "dist-release"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    artifacts = list(DIST.glob("shift_scenario_lab-0.1.0*"))
    if not artifacts:
        raise SystemExit("build artifacts are missing; run python -m build first")
    RELEASE.mkdir(exist_ok=True)
    copied = []
    for artifact in artifacts:
        destination = RELEASE / artifact.name
        shutil.copy2(artifact, destination)
        copied.append(destination)
    for sample in (ROOT / "examples/demo-report.json", ROOT / "examples/synthetic_credit.csv"):
        destination = RELEASE / sample.name
        shutil.copy2(sample, destination)
        copied.append(destination)
    wheel = next(item for item in copied if item.suffix == ".whl")
    with tempfile.TemporaryDirectory() as directory:
        environment = {"PYTHONPATH": directory}
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--target",
                directory,
                str(wheel),
            ],
            check=True,
            cwd=ROOT,
        )
        subprocess.run(
            [sys.executable, "-c", "import shift_scenario_lab; print(shift_scenario_lab.__all__)"],
            check=True,
            cwd=directory,
            env={**dict(__import__("os").environ), **environment},
        )
    checksums = "\n".join(f"{sha256(item)}  {item.name}" for item in sorted(copied)) + "\n"
    (RELEASE / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")
    print(f"Packaged {len(copied)} release assets in {RELEASE}")


if __name__ == "__main__":
    main()
