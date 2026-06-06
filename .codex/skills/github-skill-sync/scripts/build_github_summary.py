#!/usr/bin/env python3
"""Build a GitHub-ready sync summary from a read-only workspace scan."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from scan_skills import scan  # noqa: E402


def bullet(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def build_summary(data: dict[str, object]) -> str:
    skills = data["skill_inventory"]
    bug_libraries = data["bug_library_inventory"]
    files = data["file_inventory"]

    by_rec: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in files:
        by_rec[str(item["recommendation"])].append(item)

    skill_lines = [
        f"`{item['name']}` ({item['source']}): `{item['path']}`"
        for item in skills
    ]
    bug_lines = [
        f"`{item['name']}` ({item['source']}): `{item['path']}`"
        for item in bug_libraries
    ]
    recommended_lines = [
        f"`{item['path']}`"
        for item in by_rec.get("upload_recommended", [])
    ]
    caution_lines = [
        f"`{item['path']}`: {item['reason']} ({', '.join(item['findings']) or 'review recommended'})"
        for item in by_rec.get("upload_with_caution", [])
    ]
    excluded_lines = [
        f"`{item['path']}`: {item['reason']}"
        for item in by_rec.get("do_not_upload", [])
    ]

    return f"""# GitHub Skill Sync Review

## Skill Inventory

{bullet(skill_lines)}

## Bug Library Inventory

{bullet(bug_lines)}

## Upload Recommended

{bullet(recommended_lines)}

## Upload With Caution

{bullet(caution_lines)}

## Do Not Upload

{bullet(excluded_lines)}

## GitHub Commit Message

```text
Sync skills and project records

- Add or update project and Codex skill records
- Include GitHub-ready sync summaries
- Review sensitive outputs, keys, and local artifacts before upload
```

## GitHub Comment Draft

```markdown
## Skill Updates

- Prepared a skill inventory covering workspace skills and user-maintained Codex skills.
- Detected bug-library skills for Python and SQL knowledge capture.

## Project Updates

- Reviewed workspace files and grouped them by upload recommendation.

## Bug Library / Learning Notes

- Bug libraries are recommended for private GitHub versioning after redaction.
- Store schemas, prevention rules, fix summaries, and validation checks; avoid raw secrets and proprietary data.

## Risk Review

- Safe to upload: source, README, configs, sample files, and redacted skill records.
- Needs caution: generated reports, Supabase configuration, URLs, local network addresses, and HTML outputs.
- Excluded: local system files, `.env`, credentials, and unredacted logs/data.

## Next Step

- Confirm the upload scope, then run the approved Git add/commit/push workflow.
```

## Approval Required Actions

- `git add` selected files.
- `git commit` with the approved commit message.
- Configure GitHub remote if missing.
- `git push` to the approved branch.
- Post GitHub issue/PR comment only if the user provides or approves the target.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GitHub-ready sync summary.")
    parser.add_argument("--workspace", default=".", help="Workspace root to scan.")
    parser.add_argument("--skills-root", default="~/.codex/skills", help="Codex skills root.")
    parser.add_argument("--include-system", action="store_true", help="Include .system skills.")
    parser.add_argument("--json-out", help="Optional path for raw scan JSON.")
    args = parser.parse_args()

    data = scan(Path(args.workspace), Path(args.skills_root), args.include_system)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(build_summary(data))


if __name__ == "__main__":
    main()
