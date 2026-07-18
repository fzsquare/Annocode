#!/usr/bin/env python3
"""Scan a repository for ANNOCODE-CHANGE markers belonging to a requirement ID."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MARKER = re.compile(r"ANNOCODE-CHANGE(?:-IMPLEMENTED)?\[([a-z][a-z0-9-]{2,63})/([A-Z][0-9]+)\]")
EXCLUDED_DIRS = {
    ".git", ".annocode", ".agents", ".codex", "node_modules", "vendor",
    "dist", "build", "target", ".venv", "venv", "__pycache__", ".next",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--requirement", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    results: list[dict[str, object]] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for match in MARKER.finditer(line):
                if match.group(1) == args.requirement:
                    results.append({"requirement": match.group(1), "task": match.group(2), "file": str(path.relative_to(root)), "line": number, "marker": match.group(0)})
    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(f"{item['file']}:{item['line']} {item['marker']}")
        print(f"Total markers: {len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
