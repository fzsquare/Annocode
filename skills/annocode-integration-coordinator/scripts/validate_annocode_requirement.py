#!/usr/bin/env python3
"""Validate an Annocode requirement workspace and its role handoffs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED = [
    "README.md", "MANIFEST.md", "REQUEST.md", "PROTOCOL.md", "10-plan.md",
    "20-task-board.md", "30-annotations.md", "40-integration.md",
    "50-test-report.md", "60-acceptance.md", "70-final.md",
]
EXCLUDED_DIRS = {
    ".git", ".annocode", ".agents", ".codex", "node_modules", "vendor",
    "dist", "build", "target", ".venv", "venv", "__pycache__", ".next",
}
MARKER = re.compile(r"ANNOCODE-CHANGE(?:-IMPLEMENTED)?\[([a-z][a-z0-9-]{2,63})/([A-Z][0-9]+)\]")
TASK = re.compile(r"T[0-9]+\.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--requirement", required=True)
    parser.add_argument("--phase", choices=("init", "plan", "final"), default="init")
    return parser.parse_args()


def contains(path: Path, text: str) -> bool:
    return path.is_file() and text in path.read_text(encoding="utf-8")


def unresolved_markers(root: Path, requirement: str) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            body = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(body.splitlines(), 1):
            for match in MARKER.finditer(line):
                if match.group(1) == requirement:
                    hits.append(f"{path.relative_to(root)}:{number} {match.group(0)}")
    return hits


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve()
    ws = root / ".annocode" / "requirements" / args.requirement
    errors: list[str] = []

    if not ws.is_dir():
        errors.append(f"missing workspace: {ws}")
    else:
        for name in REQUIRED:
            if not (ws / name).is_file():
                errors.append(f"missing required file: {name}")
        request = ws / "REQUEST.md"
        if request.is_file() and "PENDING: Orchestrator must write" in request.read_text(encoding="utf-8"):
            errors.append("REQUEST.md does not contain the user request")

    if args.phase in {"plan", "final"} and ws.exists():
        if not contains(ws / "handoffs/01-planner-to-annotator.md", "Status: COMPLETE"):
            errors.append("Planner handoff is not COMPLETE")
        tasks = sorted(p for p in (ws / "tasks").glob("T*.md") if TASK.fullmatch(p.name)) if (ws / "tasks").exists() else []
        if not tasks:
            errors.append("no concrete task contracts found")

    if args.phase == "final" and ws.exists():
        if not contains(ws / "handoffs/02-annotator-to-orchestrator.md", "Status: COMPLETE"):
            errors.append("Annotator handoff is not COMPLETE")
        tasks = sorted(p for p in (ws / "tasks").glob("T*.md") if TASK.fullmatch(p.name))
        for task in tasks:
            handoffs = list((ws / "handoffs/implementers").glob(f"{task.stem}-A*.md"))
            if not any(contains(p, "Status: READY_FOR_INTEGRATION") for p in handoffs):
                errors.append(f"no READY_FOR_INTEGRATION handoff for {task.stem}")
        if not contains(ws / "handoffs/03-integration-to-test.md", "Status: READY_FOR_TEST"):
            errors.append("Integration handoff is not READY_FOR_TEST")
        if not contains(ws / "handoffs/04-test-to-acceptance.md", "Status: TESTS_COMPLETE"):
            errors.append("Test handoff is not TESTS_COMPLETE")
        if not contains(ws / "handoffs/05-acceptance-to-orchestrator.md", "Verdict: PASS"):
            errors.append("Acceptance handoff is not PASS")
        if not contains(ws / "60-acceptance.md", "Verdict: PASS"):
            errors.append("60-acceptance.md is not PASS")
        if not contains(ws / "70-final.md", "Decision: PASS"):
            errors.append("70-final.md is not PASS")
        for hit in unresolved_markers(root, args.requirement):
            errors.append(f"unresolved marker: {hit}")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALIDATION PASSED: {ws} ({args.phase})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
