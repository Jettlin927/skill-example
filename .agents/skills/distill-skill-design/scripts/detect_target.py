#!/usr/bin/env python3
"""
Detect candidate target files for the skill-design TL;DR install.

Outputs JSON to stdout listing each candidate's existence, size, and writability.
Cross-platform: uses pathlib.Path.home() so it works on macOS, Linux, and Windows
without depending on shell ~ expansion.

Usage:
    python3 detect_target.py
    python detect_target.py        # Windows fallback
    py -3 detect_target.py         # Windows Python launcher

No arguments. No side effects (does not create or modify any files).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def inspect(name: str, parts: tuple[str, ...]) -> dict:
    home = Path.home()
    target = home.joinpath(*parts)
    exists = target.exists()
    size = target.stat().st_size if exists else 0
    # If the file exists, check whether it's directly writable;
    # otherwise check whether its parent (or home, if parent missing) is writable.
    if exists:
        writable = os.access(str(target), os.W_OK)
    elif target.parent.exists():
        writable = os.access(str(target.parent), os.W_OK | os.X_OK)
    else:
        writable = os.access(str(home), os.W_OK | os.X_OK)
    return {
        "name": name,
        "path": str(target),
        "exists": exists,
        "size_bytes": size,
        "writable": writable,
    }


def main() -> int:
    result = {
        "platform": sys.platform,
        "home": str(Path.home()),
        "candidates": [
            inspect("claude", (".claude", "CLAUDE.md")),
            inspect("codex",  (".codex",  "AGENTS.md")),
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
