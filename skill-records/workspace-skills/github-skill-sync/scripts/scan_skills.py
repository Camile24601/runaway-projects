#!/usr/bin/env python3
"""Read-only scanner for project and user Codex skills."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SENSITIVE_PATTERNS = [
    ("env_file", re.compile(r"(^|/)\.env(\.|$|/)")),
    ("mac_system_file", re.compile(r"(^|/)\.DS_Store$")),
    ("supabase_project", re.compile(r"https://[a-z0-9-]+\.supabase\.co|sb_publishable_[A-Za-z0-9_]+|sb_secret_[A-Za-z0-9_]+", re.I)),
    ("assigned_secret", re.compile(r"(api[_-]?key|secret|token|password|passwd)\s*[:=]\s*[\"'][^\"']{8,}[\"']", re.I)),
    ("known_token_prefix", re.compile(r"\b(ghp_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b")),
    ("local_network_address", re.compile(r"\b192\.168\.\d+\.\d+\b")),
    ("url", re.compile(r"https?://", re.I)),
]


@dataclass
class SkillRecord:
    name: str
    path: str
    source: str
    description: str
    is_system: bool = False


def read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8")[:limit]
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("\"'")
    return result


def iter_files(root: Path) -> Iterable[Path]:
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__"}
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in skip_dirs]
        for filename in filenames:
            yield Path(current_root) / filename


def collect_project_skills(workspace: Path) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for path in iter_files(workspace):
        if path.name != "SKILL.md":
            continue
        rel_parts = path.relative_to(workspace).parts if path.is_relative_to(workspace) else path.parts
        if "skill-records" in rel_parts:
            continue
        text = read_text(path)
        meta = parse_frontmatter(text)
        records.append(
            SkillRecord(
                name=meta.get("name") or path.parent.name,
                path=str(path),
                source="workspace",
                description=meta.get("description", ""),
                is_system=False,
            )
        )
    return records


def collect_global_skills(skills_root: Path, include_system: bool) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    if not skills_root.exists():
        return records
    for path in skills_root.rglob("SKILL.md"):
        is_system = ".system" in path.parts
        if is_system and not include_system:
            continue
        text = read_text(path)
        meta = parse_frontmatter(text)
        records.append(
            SkillRecord(
                name=meta.get("name") or path.parent.name,
                path=str(path),
                source="global",
                description=meta.get("description", ""),
                is_system=is_system,
            )
        )
    return records


def classify_file(path: Path, workspace: Path) -> dict[str, object]:
    rel = path.relative_to(workspace).as_posix() if path.is_relative_to(workspace) else str(path)
    findings: list[str] = []
    text = ""
    if path.is_file() and path.stat().st_size <= 500_000:
        text = read_text(path)
    haystack = f"{rel}\n{text[:50_000]}"
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(haystack):
            findings.append(label)

    recommendation = "upload_recommended"
    reason = "source or documentation file"
    if rel.endswith(".DS_Store") or ".env" in rel or rel == "mood-journal/config.js":
        recommendation = "do_not_upload"
        reason = "local system, secret, or environment file"
    elif rel.startswith("finance-bi-local/output/"):
        recommendation = "do_not_upload"
        reason = "generated report output"
    elif findings:
        recommendation = "upload_with_caution"
        reason = "contains URLs, assigned secrets, local addresses, or generated credentials"
    elif "/output/" in f"/{rel}" or rel.endswith(".html"):
        recommendation = "upload_with_caution"
        reason = "generated output or inspectable HTML artifact"

    return {
        "path": rel,
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "recommendation": recommendation,
        "reason": reason,
        "findings": findings,
    }


def scan(workspace: Path, skills_root: Path, include_system: bool = False) -> dict[str, object]:
    workspace = workspace.resolve()
    skills_root = skills_root.expanduser().resolve()
    project_skills = collect_project_skills(workspace)
    global_skills = collect_global_skills(skills_root, include_system)
    files = [classify_file(path, workspace) for path in iter_files(workspace)]
    bug_libraries = [
        asdict(skill)
        for skill in global_skills + project_skills
        if "bug" in skill.name.lower() or "bug-library" in skill.path.lower()
    ]
    return {
        "workspace": str(workspace),
        "skills_root": str(skills_root),
        "skill_inventory": [asdict(skill) for skill in sorted(project_skills + global_skills, key=lambda item: (item.source, item.name))],
        "bug_library_inventory": bug_libraries,
        "file_inventory": sorted(files, key=lambda item: str(item["path"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan project files and Codex skills without modifying anything.")
    parser.add_argument("--workspace", default=".", help="Workspace root to scan.")
    parser.add_argument("--skills-root", default="~/.codex/skills", help="Codex skills root.")
    parser.add_argument("--include-system", action="store_true", help="Include .system skills.")
    args = parser.parse_args()

    result = scan(Path(args.workspace), Path(args.skills_root), args.include_system)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
