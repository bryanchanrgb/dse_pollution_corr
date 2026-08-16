"""Bootstrap entry point for repo-root eval package."""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    root = Path(__file__).resolve().parents[2]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    from eval.run import main as eval_main

    eval_main(argv)
