#!/usr/bin/env python3
"""Build a lightweight evidence index from a resume and local project files."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".sql",
    ".html",
    ".css",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
}

TAG_PATTERNS = {
    "python": [r"\bpython\b", r"\.py\b", r"\bpandas\b", r"\bxlwings\b", r"\bopenpyxl\b"],
    "excel-automation": [r"\bexcel\b", r"\bxlsx?\b", r"\bxlwings\b", r"\bopenpyxl\b", r"workbook", r"worksheet"],
    "sap": [r"\bsap\b", r"\bpyautogui\b", r"\bwin32gui\b", r"\btcode\b", r"\bzmm\d+\b"],
    "data-cleaning": [r"\bclean", r"\btransform", r"\bfilter", r"\bmerge", r"\bmatch", r"\bjoin", r"\bpandas\b"],
    "reporting": [r"\breport", r"\bdashboard", r"\bbi\b", r"\btemplate", r"\bsummary"],
    "finance-procurement": [r"\bfinance\b", r"\b采购\b", r"\b采购订单\b", r"\bpo\b", r"\border\b", r"\b供应商\b"],
    "automation": [r"\bautomation\b", r"\bautomate", r"\b自动化\b", r"\bbatch\b", r"\bworkflow\b"],
    "documents": [r"\bdocx\b", r"\bpptx\b", r"\bdocument\b", r"\bpresentation\b"],
    "frontend": [r"\breact\b", r"\bvue\b", r"\bhtml\b", r"\bcss\b", r"\bfrontend\b", r"\bthree\.js\b"],
}


def read_text_file(path: Path, max_chars: int) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except OSError:
        return ""


def read_docx(path: Path, max_chars: int) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (OSError, KeyError, zipfile.BadZipFile):
        return ""
    root = ElementTree.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    chunks = [node.text or "" for node in root.findall(".//w:t", ns)]
    return "\n".join(chunks)[:max_chars]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tags_for(text: str) -> list[str]:
    lowered = text.lower()
    tags: list[str] = []
    for tag, patterns in TAG_PATTERNS.items():
        if any(re.search(pattern, lowered, re.IGNORECASE) for pattern in patterns):
            tags.append(tag)
    return tags


def snippets_for(text: str, tags: list[str], max_snippets: int = 4) -> list[str]:
    lines = [normalize(line) for line in text.splitlines() if normalize(line)]
    snippets: list[str] = []
    for line in lines:
        lowered = line.lower()
        if any(tag.replace("-", " ") in lowered or tag in lowered for tag in tags):
            snippets.append(line[:240])
        elif any(keyword in lowered for keyword in ("pandas", "xlwings", "sap", "excel", "report", "自动化", "采购")):
            snippets.append(line[:240])
        if len(snippets) >= max_snippets:
            break
    return snippets


def iter_project_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            files.append(path)
    return files


def build_index(project_root: Path | None, resume: Path | None, max_chars: int) -> dict:
    evidence: dict = {
        "resume": None,
        "projects": [],
        "tag_summary": {},
    }

    if resume:
        text = read_docx(resume, max_chars) if resume.suffix.lower() == ".docx" else read_text_file(resume, max_chars)
        resume_tags = tags_for(text + " " + resume.name)
        evidence["resume"] = {
            "path": str(resume),
            "tags": resume_tags,
            "snippets": snippets_for(text, resume_tags, 8),
            "text_preview": normalize(text)[:1200],
        }
        for tag in resume_tags:
            evidence["tag_summary"][tag] = evidence["tag_summary"].get(tag, 0) + 3

    if project_root:
        for path in iter_project_files(project_root):
            text = read_text_file(path, max_chars)
            combined = f"{path.name}\n{text}"
            file_tags = tags_for(combined)
            if not file_tags:
                continue
            item = {
                "path": str(path),
                "tags": file_tags,
                "snippets": snippets_for(text, file_tags),
                "evidence_strength": "medium" if path.suffix.lower() in {".md", ".py"} else "weak",
            }
            evidence["projects"].append(item)
            for tag in file_tags:
                evidence["tag_summary"][tag] = evidence["tag_summary"].get(tag, 0) + 1

    evidence["projects"].sort(key=lambda item: (-len(item["tags"]), item["path"]))
    evidence["tag_summary"] = dict(sorted(evidence["tag_summary"].items(), key=lambda pair: (-pair[1], pair[0])))
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, help="Folder containing local/Codex projects to scan.")
    parser.add_argument("--resume", type=Path, help="Master resume in txt, md, or docx format.")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON evidence index.")
    parser.add_argument("--max-chars", type=int, default=50000, help="Maximum characters to read from each file.")
    args = parser.parse_args()

    if not args.project_root and not args.resume:
        raise SystemExit("Provide --project-root, --resume, or both.")

    evidence = build_index(args.project_root, args.resume, args.max_chars)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote evidence index to {args.out}")
    print("Top tags:", ", ".join(list(evidence["tag_summary"].keys())[:12]) or "none")


if __name__ == "__main__":
    main()
