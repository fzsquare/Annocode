#!/usr/bin/env python3
"""Install Annocode 1.0.0 Skills for one project or the current user."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

VERSION = "1.0.0"
SKILL_PREFIX = "annocode-"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--project", metavar="PATH", help="install into PATH/.agents/skills")
    target.add_argument("--user", action="store_true", help="install into ~/.agents/skills")
    parser.add_argument("--force", action="store_true", help="replace existing Annocode Skills")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = Path(__file__).resolve().parent / "skills"
    destination_root = (
        Path.home() / ".agents" / "skills"
        if args.user
        else Path(args.project).resolve() / ".agents" / "skills"
    )
    destination_root.mkdir(parents=True, exist_ok=True)

    sources = sorted(path for path in source_root.iterdir() if path.is_dir())
    invalid = [path.name for path in sources if not path.name.startswith(SKILL_PREFIX)]
    if invalid:
        raise SystemExit(f"invalid Skill directories: {', '.join(invalid)}")

    for source in sources:
        destination = destination_root / source.name
        if destination.exists() and not args.force:
            print(f"SKIP {source.name}: destination exists (use --force to update)")
            continue
        shutil.copytree(source, destination, dirs_exist_ok=args.force)
        print(f"INSTALLED {source.name} -> {destination}")

    print(f"Annocode {VERSION} installed. Restart Codex to load the Skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
