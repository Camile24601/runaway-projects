---
name: sql-bug-library
description: Record, classify, and propose reusable prevention rules for SQL bugs, wrong-result queries, silent data issues, join or aggregation mistakes, schema drift, performance regressions, and database behavior surprises. Use when SQL fails with an error or when SQL returns plausible but incorrect, incomplete, duplicated, stale, or slow results.
---

# SQL Bug Library

## Core Principle

SQL bugs are not limited to thrown errors. Many serious SQL issues are silent: duplicated rows, missing rows, wrong joins, incorrect aggregation, stale dimensions, implicit casts, timezone drift, NULL behavior, or performance plans that make a workflow unusable.

This skill records reusable SQL bug knowledge and proposes prevention rules. It does not replace SQL development, testing, or review skills.

Every SQL bug entry must identify whether the issue was an explicit error or a silent wrong-result problem.

## Trigger Conditions

Use this skill when:

- SQL execution raises syntax, permission, connection, schema, type, constraint, deadlock, timeout, or resource errors.
- A query runs but returns wrong totals, duplicated rows, missing records, unexpected NULLs, wrong dates, wrong periods, wrong filters, wrong grain, or stale data.
- A query is too slow, uses an unexpected plan, scans too much data, or breaks an expected index/partition strategy.
- A schema, column meaning, business definition, or upstream table changed and an existing query became stale.
- The user asks to fix a SQL result that "looks wrong" even without an error message.
- A SQL issue should become a review checklist, testing rule, or coding prevention rule.

## Bug Entry Schema

Use YAML:

```yaml
bug_entry:
  id: "sqlbug-YYYYMMDD-HHMMSS-short-title"
  status: "proposed"
  language: "sql"
  title: ""
  severity: "critical | high | medium | low"
  issue_mode: "explicit_error | silent_wrong_result | performance | schema_drift | business_rule_drift"
  source:
    task_summary: ""
    database_or_engine: ""
    query_or_model: ""
    user_reported: true
  symptom:
    error_message: ""
    wrong_result_summary: ""
    expected_result: ""
    observed_result: ""
  root_cause:
    category: "syntax | permission | missing_table | missing_column | type_cast | null_semantics | join_grain | aggregation | filter_logic | date_time | window_function | cte_order | transaction | index | partition | schema_drift | business_definition | unknown"
    explanation: ""
  decomposition_link:
    caused_by: "premature_querying | missing_grain_check | missing_reconciliation | unclear_boundary | missing_handoff | environment_assumption | insufficient_sample_data | review_gap | unknown"
    explanation: ""
  fix:
    fix_summary: ""
    safer_query_pattern: ""
    prevention_rule: ""
  validation:
    checks:
      - "row_count"
      - "distinct_key_count"
      - "total_reconciliation"
      - "sample_trace"
      - "null_check"
      - "date_range_check"
      - "explain_plan"
    evidence: ""
  skill_updates:
    should_update_other_skills: false
    targets:
      - skill: ""
        proposed_rule: ""
  tags:
    - ""
```

## Silent SQL Bug Checks

For SQL issues without an error message, prioritize:

- Grain check: What is one row supposed to represent?
- Join key check: Are keys unique on the expected side?
- Duplication check: Did joins multiply rows?
- Missing-row check: Did inner joins remove expected records?
- NULL check: Did `NULL` change filter, join, or calculation behavior?
- Date/period check: Are timezones, inclusive/exclusive ranges, fiscal periods, and string dates correct?
- Aggregation check: Are grouped fields and measures at compatible grains?
- Reconciliation check: Do totals match trusted source totals?
- Schema drift check: Did column names, types, meanings, or upstream filters change?
- Performance check: Did the query scan unexpected partitions or ignore indexes?

## Decomposition Link Categories

- `premature_querying`: Query was written before confirming grain, keys, source tables, or business definitions.
- `missing_grain_check`: Workflow did not explicitly validate row grain before joins or aggregation.
- `missing_reconciliation`: No totals, counts, or sample trace were planned.
- `unclear_boundary`: SQL, Python transformation, dashboard logic, or manual Excel logic boundaries were unclear.
- `missing_handoff`: Upstream process did not provide required table contracts, keys, partitions, or refresh timing.
- `environment_assumption`: Query assumed a database engine, collation, timezone, permission, or SQL dialect behavior.
- `insufficient_sample_data`: Available examples did not include duplicates, NULLs, late data, or boundary dates.
- `review_gap`: Review failed to catch a known SQL risk pattern.

## Output Format

Return:

```yaml
sql_bug_library_review:
  should_record: true
  priority: "P0 | P1 | P2 | P3"
  bug_entry: {}
  recommended_actions:
    - "record_in_sql_bug_library"
    - "update_related_skill"
  needs_user_confirmation: true
```

If no entry is needed:

```yaml
sql_bug_library_review:
  should_record: false
  reason: ""
```

## Storage Guidance

If the user approves persistent storage, append the entry to the chosen bug record file or create one project-level SQL bug log. Keep full wrong-result evidence in the SQL bug library and add only concise prevention rules to SQL review, testing, or coding skills.

Do not store secrets, credentials, private connection strings, or full proprietary datasets in bug entries.
