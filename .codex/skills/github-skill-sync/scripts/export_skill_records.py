#!/usr/bin/env python3
"""Export user-maintained Codex skill records into the workspace for GitHub versioning."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from scan_skills import scan  # noqa: E402


def write_text(path: Path, text: str, write: bool) -> None:
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def copy_file(src: Path, dest: Path, write: bool) -> None:
    if write:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def build_registry(skills: list[dict[str, object]], bug_libraries: list[dict[str, object]]) -> str:
    lines = [
        "# Skill Registry",
        "",
        "This registry is generated from workspace and user-maintained Codex skills for GitHub review.",
        "System skills under `.system` are excluded by default.",
        "",
        "## Skills",
        "",
    ]
    for item in skills:
        lines.append(f"- `{item['name']}` ({item['source']}): `{item['path']}`")
        description = str(item.get("description") or "").strip()
        if description:
            lines.append(f"  - {description}")
    lines.extend(["", "## Bug Libraries", ""])
    if bug_libraries:
        for item in bug_libraries:
            lines.append(f"- `{item['name']}` ({item['source']}): `{item['path']}`")
    else:
        lines.append("- None detected.")
    lines.append("")
    return "\n".join(lines)


def export_records(workspace: Path, skills_root: Path, output_dir: Path, write: bool) -> list[str]:
    data = scan(workspace, skills_root, include_system=False)
    exported: list[str] = []
    output_dir = workspace / output_dir

    for item in data["skill_inventory"]:
        src = Path(str(item["path"]))
        if not src.exists():
            continue
        source = str(item["source"])
        name = str(item["name"])
        if source == "global":
            dest = output_dir / "codex-skills" / name / "SKILL.md"
        else:
            dest = output_dir / "workspace-skills" / name / "SKILL.md"
        copy_file(src, dest, write)
        exported.append(str(dest.relative_to(workspace)))

    registry = build_registry(data["skill_inventory"], data["bug_library_inventory"])
    registry_path = output_dir / "skill-registry.md"
    write_text(registry_path, registry, write)
    exported.append(str(registry_path.relative_to(workspace)))

    return exported


def main() -> None:
    parser = argparse.ArgumentParser(description="Export skill records to a GitHub-versioned workspace folder.")
    parser.add_argument("--workspace", default=".", help="Workspace root.")
    parser.add_argument("--skills-root", default="~/.codex/skills", help="Codex skills root.")
    parser.add_argument("--output-dir", default="skill-records", help="Workspace-relative export folder.")
    parser.add_argument("--write", action="store_true", help="Actually write files. Omit for dry run.")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    skills_root = Path(args.skills_root).expanduser().resolve()
    exported = export_records(workspace, skills_root, Path(args.output_dir), args.write)
    mode = "wrote" if args.write else "would write"
    for path in exported:
        print(f"{mode}: {path}")


if __name__ == "__main__":
    main()
