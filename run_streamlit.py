from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(root / "Home.py"),
            "--browser.gatherUsageStats",
            "false",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
