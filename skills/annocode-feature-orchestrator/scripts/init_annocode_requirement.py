#!/usr/bin/env python3
"""Initialize an Annocode clean-context workspace for a user-specified requirement ID."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

MAIN_FILES = [
    "README.md", "MANIFEST.md", "REQUEST.md", "PROTOCOL.md", "10-plan.md",
    "20-task-board.md", "30-annotations.md", "40-integration.md",
    "50-test-report.md", "60-acceptance.md", "70-final.md",
]
COPIES = {
    "TASK-TEMPLATE.md": "tasks/TEMPLATE.md",
    "01-PLANNER.md": "handoffs/01-planner-to-annotator.md",
    "02-ANNOTATOR.md": "handoffs/02-annotator-to-orchestrator.md",
    "IMPLEMENTER.md": "handoffs/implementers/TEMPLATE.md",
    "03-INTEGRATION.md": "handoffs/03-integration-to-test.md",
    "04-TEST.md": "handoffs/04-test-to-acceptance.md",
    "05-ACCEPTANCE.md": "handoffs/05-acceptance-to-orchestrator.md",
    "REWORK.md": "handoffs/rework/TEMPLATE.md",
}
ID_PATTERN = re.compile(r"[a-z][a-z0-9-]{2,63}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirement_id")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--title", default=None)
    parser.add_argument("--request-file", default=None, help="UTF-8 file containing the exact user request")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not ID_PATTERN.fullmatch(args.requirement_id):
        raise SystemExit("requirement_id must match [a-z][a-z0-9-]{2,63}")

    root = Path(args.root).resolve()
    annocode_root = root / ".annocode"
    requirements_root = annocode_root / "requirements"
    workspace = requirements_root / args.requirement_id
    templates = Path(__file__).resolve().parents[1] / "assets" / "templates"
    title = args.title or args.requirement_id.replace("-", " ").title()
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    request = "PENDING: Orchestrator must write the exact user request before spawning Planner."
    if args.request_file:
        request = Path(args.request_file).read_text(encoding="utf-8").strip()
        if not request:
            raise SystemExit("request file is empty")

    if workspace.exists() and args.request_file and (workspace / "REQUEST.md").is_file():
        existing_request = (workspace / "REQUEST.md").read_text(encoding="utf-8")
        if request not in existing_request:
            raise SystemExit("requirement_id already exists with a different request; choose a new ID")

    workspace.mkdir(parents=True, exist_ok=True)
    for relative in ("tasks", "handoffs/implementers", "handoffs/rework", "artifacts"):
        (workspace / relative).mkdir(parents=True, exist_ok=True)

    replacements = {
        "{{REQUIREMENT_ID}}": args.requirement_id,
        "{{TITLE}}": title,
        "{{CREATED_AT}}": created_at,
        "{{USER_REQUEST}}": request,
    }
    created: list[Path] = []
    skipped: list[Path] = []

    def render(source_name: str, destination_name: str) -> None:
        destination = workspace / destination_name
        if destination.exists():
            skipped.append(destination)
            return
        text = (templates / source_name).read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        destination.write_text(text, encoding="utf-8")
        created.append(destination)

    for name in MAIN_FILES:
        render(name, name)
    for source, destination in COPIES.items():
        render(source, destination)

    registry = annocode_root / "REGISTRY.md"
    if not registry.exists():
        registry.write_text("# Requirement Registry\n\n| Requirement-ID | Title | Status | Created |\n|---|---|---|---|\n", encoding="utf-8")
    registry_text = registry.read_text(encoding="utf-8")
    if not re.search(rf"\|\s*{re.escape(args.requirement_id)}\s*\|", registry_text):
        safe_title = title.replace("|", "\\|")
        with registry.open("a", encoding="utf-8") as handle:
            handle.write(f"| {args.requirement_id} | {safe_title} | INITIALIZED | {created_at} |\n")

    print(f"Annocode requirement workspace: {workspace}")
    for path in created:
        print(f"CREATED {path.relative_to(root)}")
    for path in skipped:
        print(f"SKIPPED existing {path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
