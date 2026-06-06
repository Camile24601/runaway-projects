---
name: career-project-jd-matcher
description: Match a user's master resume and real Codex/local project history against job descriptions, recommend jobs to apply for, discover JD directions that fit the user's actual project evidence, and draft JD-tailored resume content without fabricating experience. Use when the user wants resume tailoring, job JD screening, project-to-resume packaging, evidence-backed resume bullets, or reverse job-search suggestions based on completed local/Codex projects.
---

# Career Project JD Matcher

## Overview

Use this skill to turn a master resume plus real local/Codex project work into an evidence-backed job application workflow. Optimize resumes by selecting, reordering, and rewriting true facts; never invent employers, dates, degrees, certifications, outcomes, scale, metrics, responsibilities, or tools that are not supported by evidence.

## Core Workflow

1. Clarify inputs only when missing:
   - Master resume path or pasted resume text.
   - JD source: pasted JD, text/Markdown/HTML files, URLs provided by the user, or a directory of saved JDs.
   - Project evidence source: usually the current workspace or a project folder.
   - Target geography/language/style if the user cares.
2. Build or update the evidence base:
   - Run `scripts/build_evidence_index.py` on the project folder when local project evidence should be considered.
   - Include the master resume as the highest-trust source.
   - Treat code, READMEs, generated reports, scripts, filenames, and user-confirmed project notes as evidence.
3. Analyze JD requirements:
   - Extract hard requirements, preferred requirements, responsibilities, business domain, tools, keywords, and seniority signals.
   - Separate must-have requirements from nice-to-have requirements.
4. Score fit:
   - Run `scripts/score_jds.py` for a deterministic keyword baseline when JD files are available.
   - Use the rubric in `references/jd_matching_rubric.md` for final judgment.
   - Produce a recommendation: `strong apply`, `apply with tailored framing`, `maybe after confirmation`, or `do not prioritize`.
5. Tailor resume content:
   - Use `references/anti_fabrication_rules.md` before drafting any resume bullet.
   - Prefer selecting and rewriting existing resume content first.
   - Add Codex/local project evidence only when the work is real and relevant.
   - Mark all unconfirmed metrics, business impact, scale, ownership level, and production usage as `needs user confirmation`.
6. Deliver outputs:
   - Job recommendation table.
   - Tailored resume bullets or a full tailored resume draft, depending on the user's request.
   - Evidence map showing which resume/project evidence supports each claim.
   - Gap list with JD requirements that should not be written into the resume.

## Evidence Priority

Use this trust order:

1. User-confirmed master resume content.
2. User-provided project notes or conversation instructions in the current turn.
3. Local project artifacts: scripts, READMEs, config files, report templates, generated outputs, tests.
4. Inferred technology/domain labels from filenames and code imports.
5. Model inference from partial evidence.

Only priorities 1-3 can directly support resume claims. Priorities 4-5 can suggest wording, questions, or search directions, but must be labeled as inference or confirmation-needed.

## Project-To-Resume Packaging

When a JD matches local project work that is absent from the master resume:

- Convert the project into a resume-safe experience only if the evidence shows real work.
- Describe the problem, tools, workflow, and deliverable.
- Avoid client/company-sensitive names unless the user explicitly allows them.
- Prefer neutral business framing: `built`, `automated`, `processed`, `standardized`, `generated`, `validated`, `documented`.
- If the project was completed with Codex assistance, describe the user's outcome and toolchain truthfully; do not imply solo authorship beyond the evidence.

Good pattern:

```text
Built a Python-based Excel automation workflow using pandas/xlwings to clean exported business data, apply rule-based matching, and generate standardized workbook outputs.
```

Avoid:

```text
Led an enterprise-wide automation transformation that improved company efficiency by 80%.
```

## Reverse JD Discovery

When the user asks which jobs fit their completed projects:

1. Build an evidence index from the workspace.
2. Extract capability tags such as `Python automation`, `Excel/xlwings`, `SAP GUI`, `pandas data cleaning`, `financial reporting`, `purchase order analysis`, `BI dashboards`, or `workflow documentation`.
3. Suggest job families and JD search keywords.
4. If browsing or a job site scan is requested, verify current results from the web or user-provided pages before naming actual openings.
5. Recommend roles based on evidence strength, not aspirational keywords.

## Script Usage

Build a project evidence index:

```bash
python3 scripts/build_evidence_index.py --project-root /path/to/projects --resume /path/to/resume.md --out evidence.json
```

Score saved JDs against the evidence index:

```bash
python3 scripts/score_jds.py --evidence evidence.json --jd-dir /path/to/jds --out job_scores.csv
```

Scripts are helpers, not final authority. Use their output as a baseline, then apply judgment and the anti-fabrication rules.

## References

- Read `references/anti_fabrication_rules.md` before generating or revising resume content.
- Read `references/jd_matching_rubric.md` before final job recommendations or reverse-search suggestions.
