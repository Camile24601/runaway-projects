---
name: skill-governance-meta-skill
description: Govern, audit, maintain, and evolve a multi-skill ecosystem after task or subagent completion. Use when completed work may contain reusable lessons, bug patterns, testing or review rules, prompt improvements, dependency changes, skill conflicts, outdated rules, duplicated guidance, or knowledge drift. This skill does not execute the original task; it produces structured YAML governance proposals for human confirmation before any skill is updated.
---

# Skill Governance Meta Skill

## Core Principle

This skill governs the skill ecosystem. It does not solve the original user task and does not directly edit skills unless the user explicitly approves a generated change proposal.

After a task or subagent finishes, decide whether the work created reusable knowledge, exposed a skill gap, changed a dependency, or revealed conflict or drift. If yes, produce a structured governance report and update proposal. If no, say so briefly and avoid adding noise to the skill system.


## User Approval Policy

When the user proposes a skill structure, implementation direction, storage layout, or governance action, treat it as a preferred hypothesis, not an irreversible instruction.

If a better option exists, propose it with tradeoffs. Do not execute file changes, skill updates, skill creation, skill splitting, skill merging, or skill deprecation until the user explicitly approves the proposed action.


## Proactive Governance Reminder

The agent should proactively surface likely skill-governance opportunities even when the user does not explicitly invoke this skill. This is especially important when a proposed learning item may update existing skills, touch multiple skills, create dependency changes, duplicate rules, introduce conflicts, or require bug-library synchronization.

When a likely governance opportunity is detected, do not edit skill files immediately. Briefly tell the user what may need governance review and ask whether to generate a structured governance proposal.

Recommended reminder format:

```text
I noticed this may affect the skill system: <brief evidence>.
Possible governance target: <skill names or dependency area>.
Would you like me to generate a structured governance proposal before changing any skill files?
```

Only persist skill updates, bug-library entries, dependency changes, splits, merges, or deprecations after explicit user confirmation.

## Trigger Gate

Run the lightweight trigger gate after a task, subagent run, review, bug fix, testing pass, prompt iteration, parsing workflow, or coding workflow finishes.

Enter full governance review only when at least one condition is true:

- A bug, exception, failed test, wrong output, environment issue, SQL result anomaly, or unexpected behavior appeared.
- The task produced a reusable rule, checklist item, verification method, prompt pattern, test pattern, parsing rule, or review heuristic.
- A skill was missing, stale, too broad, too narrow, or contradicted the observed workflow.
- Two or more skills may need coordinated updates.
- A subagent made an error that came from unclear skill instructions, missing dependency context, or wrong task attribution.
- The user says to record, remember, update a skill, add to the bug library, avoid next time, or govern the skill system.

Do not enter full governance review when:

- The task was routine and produced no reusable lesson.
- The observation is a one-off path, filename, temporary preference, or unverified guess.
- Existing skills already cover the rule and no new edge case appeared.
- The proposed update would only duplicate a rule without adding precision.

## Core Responsibilities

### 1. Update Detection

Decide whether this task produced skill-worthy knowledge.

Assess:

- Novelty: Is the lesson absent from current skills?
- Recurrence risk: Is the same issue likely to happen again?
- Impact: Would this rule reduce future bugs, rework, review misses, or prompt ambiguity?
- Evidence: Is there a concrete log, traceback, diff, failed output, test result, SQL discrepancy, or repeated user correction?
- Stability: Is the rule stable enough to encode, or should it remain a project-local note?

Output:

- `needs_update`: true, false, or needs_user_judgment.
- `reason`: concise evidence-based explanation.
- `priority`: P0, P1, P2, or P3.

Priority guide:

- P0: Prevents data loss, security exposure, destructive actions, broken production workflow, or repeated critical failure.
- P1: Prevents common wrong outputs, failed automation, incorrect SQL results, broken tests, or major review misses.
- P2: Improves reliability, decomposition, validation, maintainability, or agent handoff quality.
- P3: Nice-to-have wording, examples, cleanup, or low-risk clarification.

### 2. Skill Attribution

Identify which skill or skills should be updated.

Use single-skill attribution when the lesson belongs to one domain:

- Coding behavior -> Coding Skill.
- PDF extraction or parsing behavior -> PDF Parsing Skill.
- Python exception, environment failure, pandas/xlwings/path bug -> Python Bug Library Skill.
- SQL wrong-result, query semantics, schema, join, aggregation, or performance issue -> SQL Bug Library Skill.
- Test strategy, fixtures, assertions, coverage, CI -> Testing Skill.
- Review miss, regression risk, code review rubric -> Review Skill.
- Prompt pattern, agent instruction, ambiguity reduction -> Prompt Skill.

Use multi-skill attribution when:

- A concrete bug should be recorded in a bug library and converted into a prevention rule in a domain skill.
- A testing failure implies both Testing Skill and Coding Skill updates.
- A prompt ambiguity caused a subagent to choose the wrong skill.
- A SQL anomaly affects both SQL Bug Library and Review Skill.
- A dependency or interface change affects upstream and downstream skills.

Attribution must explain why each target skill is affected and what type of update it should receive.

### 3. Dependency Analysis

Analyze skill dependencies before proposing changes.

Dependency types:

- `requires`: Skill A cannot work without Skill B or a shared reference.
- `hands_off_to`: Skill A delegates a subtask to Skill B.
- `produces_for`: Skill A creates outputs consumed by Skill B.
- `validates`: Skill A checks artifacts produced by Skill B.
- `constrains`: Skill A sets rules another skill must obey.
- `records_failures_from`: Bug library records failures produced while another skill executes.
- `shares_rule_with`: Skills need aligned wording or shared policy.

For each proposed update, identify:

- Directly affected skills.
- Downstream skills that consume the changed output or rule.
- Upstream skills that must provide more context.
- Whether propagation is required now or can wait.
- Whether a dependency graph entry should be added or revised.

### 4. Conflict Detection

Scan likely target skills for:

- Rule conflict: Two instructions require incompatible behavior.
- Duplicate rule: Same instruction appears in multiple places without a clear owner.
- Outdated rule: A rule no longer matches current tools, environment, API, schema, or workflow.
- Mutually exclusive rule: Two skills could trigger for the same task but demand different execution paths.
- Ownership conflict: Multiple skills claim the same responsibility.
- Dependency conflict: A skill assumes an artifact or interface another skill no longer produces.

When conflict exists, do not silently choose. Produce options and recommend one owner.

Conflict handling preference:

1. Keep the complete case in the relevant bug library.
2. Put the prevention rule in the domain skill that can act before failure.
3. Put shared orchestration rules in this governance skill.
4. Avoid copying long case details into multiple skills.

### 5. Change Proposal

Generate a standard YAML proposal. The proposal is an artifact for human approval and should be specific enough to implement later.

Do not edit target skills during proposal generation unless the user explicitly says to apply the proposal.

### 6. Governance Report

Every full governance review should end with a short report covering:

- Update recommendation.
- Risk analysis.
- Affected skills.
- Dependency propagation.
- Conflict or drift findings.
- Recommended next action.

## Workflow

1. Collect task evidence:
   - Final user request.
   - Subagent output or task summary.
   - Errors, logs, diffs, tests, review comments, SQL result mismatches, or user corrections.
   - Skills invoked or skills that should have been invoked.

2. Run Update Detection:
   - Decide whether full governance review is needed.
   - If not, output `needs_update: false` with a short reason.

3. Attribute the knowledge:
   - Select one or more target skills.
   - Classify each update as `bug_case`, `rule`, `checklist`, `workflow`, `example`, `dependency`, `deprecation`, or `conflict_resolution`.

4. Analyze dependencies:
   - Identify upstream, downstream, validation, and failure-recording relationships.
   - Decide whether propagation is required.

5. Detect conflicts and drift:
   - Read only the relevant target skill files.
   - Compare the proposed rule against existing instructions.
   - Mark duplication, conflict, or outdated text.

6. Generate YAML proposal:
   - Include evidence, target skills, exact suggested changes, risk, and validation.
   - Keep proposed text concise and directly insertable.

7. Generate Governance Report:
   - Summarize what should happen now.
   - Ask for confirmation before applying changes.

8. Apply only after explicit approval:
   - Edit only the approved skill files.
   - Preserve each skill's existing style.
   - Validate the changed skill file for frontmatter, clarity, and duplication.

## Decision Tree

```text
Task or subagent finished
|
|-- Did it produce an error, wrong result, failed test, SQL anomaly, or user correction?
|   |-- yes -> Full governance review -> Bug Library attribution required
|   |-- no  -> continue
|
|-- Did it reveal a reusable rule, checklist, workflow, prompt, or review heuristic?
|   |-- yes -> Full governance review -> Domain skill attribution
|   |-- no  -> continue
|
|-- Did it expose stale, conflicting, duplicate, or missing skill guidance?
|   |-- yes -> Full governance review -> Conflict and drift analysis
|   |-- no  -> continue
|
|-- Did it affect more than one skill or a handoff between skills?
|   |-- yes -> Full governance review -> Dependency analysis
|   |-- no  -> No update
|
Full governance review
|
|-- Is evidence concrete and reusable?
|   |-- no -> needs_update: needs_user_judgment or false
|   |-- yes -> Generate YAML proposal
|
|-- Are target skills clear?
|   |-- no -> Ask user for ownership decision
|   |-- yes -> Governance report
|
|-- User approved applying?
|   |-- no -> Stop after proposal
|   |-- yes -> Edit approved skills and validate
```

## YAML Data Structure

Use this schema for change proposals:

```yaml
proposal_id: "skill-governance-YYYYMMDD-HHMMSS-short-title"
proposal_version: 1
status: "proposed"
source:
  task_summary: ""
  triggering_event: "bug | wrong_result | failed_test | reusable_rule | conflict | drift | dependency_change | user_request"
  evidence:
    - type: "traceback | log | diff | test_output | sql_result | user_feedback | review_comment | subagent_summary"
      summary: ""
      location: ""
update_detection:
  needs_update: true
  priority: "P0 | P1 | P2 | P3"
  reason: ""
  confidence: "high | medium | low"
skill_attribution:
  primary_skill: ""
  additional_skills:
    - ""
  attribution_reason:
    skill_name: ""
    reason: ""
    update_type: "bug_case | rule | checklist | workflow | example | dependency | deprecation | conflict_resolution"
dependency_analysis:
  affected_skills:
    - skill: ""
      relationship: "requires | hands_off_to | produces_for | validates | constrains | records_failures_from | shares_rule_with"
      propagation_required: true
      reason: ""
  graph_changes:
    add_edges:
      - from: ""
        to: ""
        type: ""
        reason: ""
    remove_edges:
      - from: ""
        to: ""
        reason: ""
conflict_detection:
  conflicts_found: false
  items:
    - type: "rule_conflict | duplicate_rule | outdated_rule | mutually_exclusive_rule | ownership_conflict | dependency_conflict"
      skills:
        - ""
      description: ""
      recommendation: ""
change_proposal:
  target_updates:
    - skill: ""
      file: ""
      section: ""
      operation: "add | modify | remove | replace"
      proposed_text: |
        ""
      rationale: ""
      validation: ""
risk_analysis:
  risk_level: "low | medium | high"
  risks:
    - ""
  mitigations:
    - ""
governance_report:
  summary: ""
  recommended_action: "apply | revise | defer | reject | ask_user"
  user_confirmation_needed: true
```

## Dependency Graph Design

Represent skill dependencies as directed edges.

Node fields:

```yaml
skill:
  name: ""
  category: "coding | parsing | bug_library | testing | review | prompt | governance | domain"
  owner: ""
  status: "active | deprecated | draft"
  last_reviewed: "YYYY-MM-DD"
```

Edge fields:

```yaml
edge:
  from: ""
  to: ""
  type: "requires | hands_off_to | produces_for | validates | constrains | records_failures_from | shares_rule_with"
  contract:
    input: ""
    output: ""
    required_context: ""
  drift_indicators:
    - ""
  last_verified: "YYYY-MM-DD"
```

Recommended baseline graph:

```yaml
skills:
  - name: "skill-governance-meta-skill"
    category: "governance"
  - name: "python-bug-library"
    category: "bug_library"
  - name: "sql-bug-library"
    category: "bug_library"
  - name: "Coding Skill"
    category: "coding"
  - name: "PDF Parsing Skill"
    category: "parsing"
  - name: "Testing Skill"
    category: "testing"
  - name: "Review Skill"
    category: "review"
  - name: "Prompt Skill"
    category: "prompt"
edges:
  - from: "Coding Skill"
    to: "python-bug-library"
    type: "records_failures_from"
  - from: "Testing Skill"
    to: "python-bug-library"
    type: "records_failures_from"
  - from: "Review Skill"
    to: "python-bug-library"
    type: "shares_rule_with"
  - from: "Coding Skill"
    to: "sql-bug-library"
    type: "records_failures_from"
  - from: "Review Skill"
    to: "sql-bug-library"
    type: "shares_rule_with"
  - from: "Prompt Skill"
    to: "skill-governance-meta-skill"
    type: "constrains"
  - from: "skill-governance-meta-skill"
    to: "all skills"
    type: "constrains"
```

If a repo wants persistent graph storage, keep it in a project-level governance file or a dedicated reference file. Do not scatter graph copies across many skills.

## GitHub Integration Suggestions

When the skill ecosystem is versioned in GitHub:

- Store each governance proposal as an issue or pull request checklist before applying it.
- Use labels such as `skill-governance`, `skill-update`, `bug-library`, `dependency`, `conflict`, `knowledge-drift`, `P0`, `P1`, `P2`, and `P3`.
- Use one PR per coherent governance change. Do not bundle unrelated skill updates.
- PR description should include the YAML proposal, affected skills, risk analysis, and validation performed.
- Require review for P0/P1 changes and any change that touches multiple skills.
- Add CODEOWNERS or reviewer routing by skill area when the skill set grows.
- For repeated bugs, link the bug-library entry, original failure issue, fixing PR, and prevention-rule PR.
- Use scheduled audits for stale skills: monthly for active skills, quarterly for low-use skills.

Suggested PR checklist:

```markdown
- [ ] YAML proposal included
- [ ] Affected skills listed
- [ ] Dependency graph impact checked
- [ ] Conflicts and duplicates checked
- [ ] Bug library updated when applicable
- [ ] Target skill wording kept concise
- [ ] Validation or review evidence included
```

## Subagent Invocation

Invoke this skill after subagents complete, not before the main task is understood.

Recommended subagent handoff prompt:

```text
Use $skill-governance-meta-skill to audit the completed subagent task.

Context:
- Original user request:
- Subagent role:
- Skills used:
- Output summary:
- Files changed:
- Errors or failed checks:
- User corrections:
- Tests or validation:

Return only:
1. Whether a skill update is needed.
2. YAML change proposal if needed.
3. Governance report with risks and recommended action.
Do not edit any skill files unless explicitly approved.
```

When multiple subagents ran, audit each substantial result separately, then merge proposals only if they update the same skill for the same reason.

## Required Output

For a full review, return:

```yaml
governance_review:
  needs_update: true
  priority: "P1"
  affected_skills:
    - ""
  proposal: {}
  report:
    summary: ""
    risks:
      - ""
    recommended_action: ""
```

For no update:

```yaml
governance_review:
  needs_update: false
  reason: ""
```

## Prohibitions

- Do not update skills without explicit user confirmation.
- Do not store unverified guesses as rules.
- Do not turn temporary project details into global skill instructions.
- Do not duplicate long bug cases in multiple skills.
- Do not hide conflicts by choosing one rule silently.
- Do not use this skill as a replacement for Coding, Testing, Review, PDF Parsing, Prompt, Python Bug Library, or SQL Bug Library skills.
