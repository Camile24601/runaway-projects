#!/usr/bin/env python3
"""Score saved job descriptions against an evidence index."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


TAG_KEYWORDS = {
    "python": ["python", "pandas", "numpy", "脚本"],
    "excel-automation": ["excel", "xlsx", "vlookup", "power query", "xlwings", "openpyxl", "表格"],
    "sap": ["sap", "erp", "tcode", "gui", "s/4hana"],
    "data-cleaning": ["data cleaning", "清洗", "数据处理", "etl", "merge", "match", "校验"],
    "reporting": ["report", "dashboard", "bi", "报表", "看板", "分析报告"],
    "finance-procurement": ["finance", "financial", "procurement", "purchase", "采购", "财务", "供应商"],
    "automation": ["automation", "automate", "rpa", "自动化", "流程优化"],
    "documents": ["document", "docx", "pptx", "presentation", "文档", "简报"],
    "frontend": ["react", "vue", "frontend", "html", "css", "前端"],
}


def read_jd(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def jd_tags(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            found.append(tag)
    return found


def title_from_path(path: Path, text: str) -> str:
    for line in text.splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if clean and len(clean) <= 100:
            return clean
    return path.stem


def score_one(path: Path, text: str, evidence_tags: dict[str, int]) -> dict[str, str | int]:
    tags = jd_tags(text)
    supported = [tag for tag in tags if tag in evidence_tags]
    gaps = [tag for tag in tags if tag not in evidence_tags]
    coverage = len(supported) / max(len(tags), 1)
    strength = sum(min(evidence_tags.get(tag, 0), 5) for tag in supported)
    score = min(100, round(coverage * 65 + min(strength, 20) + min(len(supported) * 3, 15)))
    if score >= 80:
        recommendation = "strong apply"
    elif score >= 65:
        recommendation = "apply with tailored framing"
    elif score >= 50:
        recommendation = "maybe after confirmation"
    else:
        recommendation = "do not prioritize"
    return {
        "job_title": title_from_path(path, text),
        "source": str(path),
        "score": score,
        "recommendation": recommendation,
        "supported_tags": ", ".join(supported),
        "gap_tags": ", ".join(gaps),
    }


def iter_jd_files(jd_dir: Path) -> list[Path]:
    exts = {".txt", ".md", ".html"}
    return sorted(path for path in jd_dir.rglob("*") if path.is_file() and path.suffix.lower() in exts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True, help="Evidence JSON from build_evidence_index.py.")
    parser.add_argument("--jd-dir", type=Path, required=True, help="Directory of saved JD text/Markdown/HTML files.")
    parser.add_argument("--out", type=Path, required=True, help="Output CSV score table.")
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    evidence_tags = {str(tag): int(weight) for tag, weight in evidence.get("tag_summary", {}).items()}
    rows = [score_one(path, read_jd(path), evidence_tags) for path in iter_jd_files(args.jd_dir)]
    rows.sort(key=lambda row: int(row["score"]), reverse=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["job_title", "source", "score", "recommendation", "supported_tags", "gap_tags"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} JD scores to {args.out}")


if __name__ == "__main__":
    main()
