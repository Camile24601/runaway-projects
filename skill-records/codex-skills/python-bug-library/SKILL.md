---
name: python-bug-library
description: Record, classify, and propose reusable prevention rules for Python bugs, exceptions, environment issues, pandas/xlwings/path problems, failed tests, and wrong Python-generated outputs. Use whenever Python code errors, a user reports a Python script failed elsewhere, a local run exposes a traceback, or a Python bug fix may need future prevention guidance.
---

# Python Bug Library

## Core Principle

This skill records reusable Python bug knowledge. It is not the primary coding skill. Use it after a Python failure or bug fix to create a structured bug-library update proposal that can be confirmed before being written into a persistent bug record or another skill.

Every Python bug entry must connect the failure to the workflow or decomposition choice that caused, exposed, or amplified it.

## Trigger Conditions

Use this skill when:

- Python raises an exception, traceback, import error, encoding error, path error, permission error, dependency error, syntax error, or runtime error.
- A test, `py_compile`, script execution, Excel automation, pandas transformation, database call, or file IO step fails.
- The user reports that a Python script failed in another environment and asks for a fix.
- Python code completes but produces wrong rows, wrong columns, wrong files, wrong formatting, wrong dates, wrong amounts, or wrong side effects.
- A bug fix produces a reusable prevention rule for Coding, Testing, Review, Prompt, or a domain skill.

## Bug Entry Schema

Use YAML:

```yaml
bug_entry:
  id: "pybug-YYYYMMDD-HHMMSS-short-title"
  status: "proposed"
  language: "python"
  title: ""
  severity: "critical | high | medium | low"
  source:
    task_summary: ""
    user_reported: true
    environment: ""
    command_or_action: ""
  symptom:
    error_type: ""
    message: ""
    traceback_summary: ""
    wrong_output_summary: ""
  root_cause:
    category: "syntax | import | dependency | path | permission | encoding | dataframe | excel | database | date | numeric | logic | environment | test | packaging | unknown"
    explanation: ""
  decomposition_link:
    caused_by: "premature_coding | over_merged_steps | over_split_steps | missing_validation | unclear_boundary | missing_handoff | environment_assumption | insufficient_sample_data | unknown"
    explanation: ""
  fix:
    changed_files:
      - ""
    fix_summary: ""
    prevention_rule: ""
  validation:
    commands:
      - ""
    evidence: ""
  skill_updates:
    should_update_other_skills: false
    targets:
      - skill: ""
        proposed_rule: ""
  tags:
    - ""
```

## Required Review Questions

Before proposing a bug entry, answer:

- Is this a real observed bug or an unverified guess?
- What exact symptom did the user or runtime observe?
- What root cause was confirmed?
- Which decomposition or workflow decision contributed to it?
- How was the fix validated?
- Should a prevention rule be added to another skill?

## Decomposition Link Categories

- `premature_coding`: Code was written before confirming fields, schema, sample data, business rules, or output format.
- `over_merged_steps`: Too many responsibilities were placed in one script or agent step.
- `over_split_steps`: The workflow was split so much that handoff files, fields, or ordering became fragile.
- `missing_validation`: The plan lacked compile checks, sample runs, assertions, row counts, amount checks, or output inspection.
- `unclear_boundary`: Coding, testing, review, parsing, SQL, Excel, or SAP responsibilities were mixed.
- `missing_handoff`: An upstream skill or subagent failed to provide required inputs to a downstream step.
- `environment_assumption`: The code assumed unavailable packages, OS behavior, permissions, Excel/SAP state, encoding, or path conventions.
- `insufficient_sample_data`: The bug came from untested edge cases or missing representative files.

## Output Format

Return:

```yaml
python_bug_library_review:
  should_record: true
  priority: "P0 | P1 | P2 | P3"
  bug_entry: {}
  recommended_actions:
    - "record_in_python_bug_library"
    - "update_related_skill"
  needs_user_confirmation: true
```

If no entry is needed:

```yaml
python_bug_library_review:
  should_record: false
  reason: ""
```

## Storage Guidance

If the user approves persistent storage, append the entry to the chosen bug record file or create one project-level bug log. Keep the complete case in the bug library and add only concise prevention rules to domain skills.

Do not store secrets, passwords, private tokens, or full proprietary datasets in bug entries.
