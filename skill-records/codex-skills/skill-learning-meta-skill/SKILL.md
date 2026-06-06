---
name: skill-learning-meta-skill
description: Learn from completed tasks, failures, repeated work, and successful patterns to discover reusable capabilities, decide whether knowledge should become a bug-library entry, an existing skill update, or a new skill, and compound concrete experience into principles, workflows, checklists, skills, and meta-skill improvements. Use after meaningful task outcomes when the goal is to make the skill system smarter, not merely to govern or audit it.
---

# Skill Learning Meta Skill

## Core Principle

This skill learns how to create, improve, split, merge, and abstract skills.

It does not manage skill conflicts, ownership, dependency propagation, or update approval as its primary job. Those belong to `skill-governance-meta-skill`.

This skill asks a deeper question after meaningful work:

> What did the system learn that could become future capability?

The output is always a learning proposal. Do not create or edit any skill until the user explicitly confirms.

## Relationship To Governance

Use this skill before governance when the question is:

- Is this experience reusable?
- Should this become a skill?
- What abstraction should be extracted?
- Is the system becoming smarter from this case?

Use `skill-governance-meta-skill` after this skill when the question is:

- Which existing skill should be updated?
- Are there conflicts, duplicates, dependencies, or drift?
- How should the approved change be safely applied?

## Core Responsibilities

### 1. Pattern Discovery

Discover repeated patterns from task records.

Scan for:

- Repeated errors: same failure mode, same environment issue, same wrong assumption.
- Repeated work: same manual steps, same code structure, same checklist, same file processing flow.
- Repeated decisions: same judgment criteria, same tradeoff, same task decomposition.
- Repeated corrections: user repeatedly clarifies the same expectation.
- Repeated validation: same tests, previews, reconciliations, or review checks.
- Repeated prompt repair: same agent ambiguity or missing instruction.

A pattern is stronger when it appears across multiple projects, multiple users, multiple files, or multiple time periods.

### 2. Skill Candidate Detection

Decide what should happen to the experience.

Allowed outcomes:

- `do_not_record`: One-off, low-confidence, temporary, or already covered.
- `add_to_bug_library`: Concrete failure case with symptom, root cause, fix, and prevention value.
- `update_existing_skill`: Existing skill can absorb the rule without becoming bloated or confused.
- `create_new_skill`: The pattern is a distinct repeatable capability with its own workflow, triggers, inputs, outputs, and validation.
- `create_reference_or_asset`: The skill exists, but needs a reusable template, checklist, sample, script, or reference file.
- `escalate_to_meta_skill`: The lesson changes how skills should be created, abstracted, or learned.

### 3. Abstraction Engine

Transform concrete cases into reusable forms.

Abstraction ladder:

```text
case
-> observed pattern
-> failure or success principle
-> repeatable checklist
-> workflow
-> skill
-> meta-skill rule
```

For each candidate, extract:

- Concrete case: What happened?
- Repeating signal: Why is it likely to happen again?
- General principle: What broader rule does it imply?
- Operational workflow: What should an agent do next time?
- Checklist: What should be verified?
- Skill form: Should this live as a skill, skill section, reference, asset, or script?

Good abstractions are:

- specific enough to change behavior;
- general enough to reuse;
- short enough to fit skill context;
- supported by evidence;
- tied to validation.

### 4. Skill Creation Framework

Create a new skill only when most of these are true:

- The task type repeats or is likely to repeat.
- It has a recognizable trigger condition.
- It has a distinct workflow, not just a single rule.
- It has specialized context Codex would not reliably infer.
- It has inputs and outputs that can be named.
- It benefits from checklists, templates, scripts, references, or assets.
- It would reduce repeated prompting, repeated bugs, or repeated decisions.
- Adding it to an existing skill would make that skill confusing or too broad.

Extend an existing skill when:

- The lesson is a small prevention rule.
- The existing skill already owns the workflow.
- The new content is a checklist item, edge case, or validation rule.
- The update will not create ownership confusion.

Do not create a new skill when:

- The content is only a bug case.
- The behavior is already covered.
- The topic is too broad and lacks workflow.
- The evidence is weak.
- The rule belongs in project docs, not global skills.
- The skill would be used only once.

### 5. Skill Evolution

Periodically review whether skills are still useful.

Review signals:

- Skill no longer triggers for real work.
- Skill repeats another skill.
- Skill has too many unrelated responsibilities.
- Skill contains stale tool, API, environment, or process assumptions.
- Skill produces too much context for too little behavior change.
- Skill has accumulated examples but no clear workflow.
- Bug library shows repeated failures despite existing rules.
- User repeatedly overrides the skill's defaults.

Evolution actions:

- `keep`: Skill is useful and current.
- `refine`: Tighten triggers, workflow, or checklist.
- `split`: Separate unrelated workflows.
- `merge`: Combine small overlapping skills.
- `deprecate`: Stop using stale skill.
- `promote`: Turn repeated reference/checklist into a full skill.
- `extract_asset`: Move repeated code/template into assets or scripts.
- `extract_reference`: Move detailed knowledge into references.

### 6. Knowledge Compounding

Use this compounding loop:

```text
Case
- A concrete success, failure, bug, review miss, or repeated workflow.

Rule
- A concise behavior change extracted from the case.

Skill
- A repeatable workflow that applies the rule before the next failure.

Meta Skill
- A higher-level learning rule about how skills should be created or improved.
```

Do not skip levels. A single case usually becomes a bug-library entry first. Multiple similar cases can become a rule. Multiple rules with a workflow can become a skill. Multiple skill-design lessons can update this meta skill.


## Proactive Learning Reminder

The agent should proactively surface likely learning opportunities even when the user does not explicitly invoke this skill. This is especially important after bug fixes, failed tests, wrong outputs, repeated workflow steps, repeated user corrections, prompt repairs, or successful patterns that look reusable.

When a likely opportunity is detected, do not update files immediately. Briefly tell the user what might be worth learning and ask whether to generate a structured learning proposal.

Recommended reminder format:

```text
I noticed a reusable learning opportunity: <brief evidence>.
Possible outcome: <bug-library entry, skill update, new skill, reference, or no record>.
Would you like me to generate a structured learning proposal before changing any files?
```

Only persist the result after explicit user confirmation.

## Workflow

1. Collect evidence:
   - Task summary.
   - What succeeded or failed.
   - Repeated steps or decisions.
   - User corrections.
   - Bugs or wrong outputs.
   - Existing skills used or missing.

2. Discover patterns:
   - Is this isolated or repeated?
   - Does it reveal a hidden workflow?
   - Did the agent repeat work that could be automated or templated?

3. Decide learning outcome:
   - Do not record.
   - Add to Bug Library.
   - Update existing Skill.
   - Create new Skill.
   - Create reference, asset, script, or checklist.
   - Update Meta Skill.

4. Abstract the case:
   - Convert case into principle, workflow, checklist, or skill candidate.

5. Score the candidate:
   - Frequency.
   - Impact.
   - Specificity.
   - Reusability.
   - Evidence quality.
   - Context cost.
   - Maintenance cost.

6. Produce proposal:
   - Output structured YAML.
   - Include recommended action.
   - Ask user confirmation before writing anything.

7. If user approves:
   - Hand off to `skill-governance-meta-skill` for conflict, dependency, and update safety review.
   - Then create or update the approved skill.

## Abstraction Rules

Prefer this mapping:

- One concrete bug -> Bug Library.
- Three similar bugs -> Existing skill prevention rule.
- Repeated workflow with stable inputs/outputs -> New or expanded skill.
- Repeated code/template -> Asset or script.
- Repeated long explanation -> Reference file.
- Repeated agent mistake -> Prompt Skill or Meta Skill update.
- Repeated review miss -> Review Skill checklist.
- Repeated validation pattern -> Testing Skill checklist or script.

A good skill abstraction must answer:

- When should this skill trigger?
- What should the agent read first?
- What steps should it follow?
- What should it never do?
- What output should it produce?
- How should success be validated?
- What should be kept out of context until needed?

## Experience Capture Standard

Record experience only when it meets at least two:

- It happened more than once.
- It caused real rework, bug, wrong output, or user correction.
- It can be prevented with a concise rule.
- It changes task decomposition.
- It creates a reusable checklist or workflow.
- It applies beyond one file or one project.
- It improves future validation.
- It reveals missing skill ownership.

Do not record:

- temporary file paths;
- secrets or credentials;
- one-off preferences;
- unverified guesses;
- project-only details with no reusable value;
- broad wisdom that does not change agent behavior.

## New Skill Creation Standard

Use this decision table:

```yaml
new_skill_decision:
  create_new_skill_when:
    - repeated_task_type: true
    - clear_trigger: true
    - distinct_workflow: true
    - specialized_context_required: true
    - reusable_outputs: true
    - validation_method_exists: true
  extend_existing_skill_when:
    - existing_owner_clear: true
    - change_is_small_rule_or_checklist: true
    - no_new_workflow_needed: true
  use_bug_library_when:
    - concrete_failure_case: true
    - symptom_root_cause_fix_known: true
  do_not_record_when:
    - one_off: true
    - weak_evidence: true
    - already_covered: true
```

## Skill Lifecycle Design

```text
candidate
-> draft
-> pilot
-> active
-> mature
-> split / merged / deprecated
```

Lifecycle states:

- `candidate`: Pattern detected, not yet proven.
- `draft`: Skill proposed, awaiting validation.
- `pilot`: Used on real tasks, still monitored.
- `active`: Reliable and useful.
- `mature`: Stable, concise, low churn.
- `split`: Too broad; divided into focused skills.
- `merged`: Too small or duplicative; merged into another skill.
- `deprecated`: Stale, unused, or superseded.

Review cadence:

- New/pilot skills: after 3 real uses.
- Active skills: monthly if frequently used.
- Mature skills: quarterly.
- Bug libraries: review after clusters of 3 similar bugs.
- Meta skills: review after repeated skill-design failures.

## YAML Output Schema

```yaml
skill_learning_review:
  review_id: "skill-learning-YYYYMMDD-HHMMSS-short-title"
  source:
    task_summary: ""
    evidence:
      - type: "success | failure | bug | repeated_work | repeated_decision | user_correction | validation"
        summary: ""
        location: ""
  pattern_discovery:
    patterns_found: true
    patterns:
      - name: ""
        type: "repeated_error | repeated_work | repeated_decision | repeated_validation | prompt_repair | workflow"
        evidence_count: 1
        recurrence_likelihood: "high | medium | low"
  candidate_detection:
    outcome: "do_not_record | add_to_bug_library | update_existing_skill | create_new_skill | create_reference_or_asset | escalate_to_meta_skill"
    reason: ""
    confidence: "high | medium | low"
  abstraction:
    concrete_case: ""
    principle: ""
    workflow: []
    checklist: []
    proposed_skill_shape:
      name: ""
      trigger: ""
      inputs: []
      outputs: []
      validation: []
  scoring:
    frequency: 1
    impact: "high | medium | low"
    specificity: "high | medium | low"
    reusability: "high | medium | low"
    evidence_quality: "high | medium | low"
    context_cost: "high | medium | low"
    maintenance_cost: "high | medium | low"
  recommendation:
    action: ""
    target_skill: ""
    needs_governance_review: true
    needs_user_confirmation: true
```

## GitHub Repository Organization

Recommended repo layout when a repository mirror is desired:

```text
/skills/
  /active/
    coding/
    testing/
    review/
    prompt/
    pdf-parsing/
  /bug-libraries/
    python-bug-library/
    sql-bug-library/
  /meta/
    governance-skill.md
    learning-skill.md
  /candidates/
    candidate-name.md
  /deprecated/
    old-skill-name.md
  /shared/
    dependency-graph.yaml
    lifecycle-register.yaml
    proposal-template.yaml
```

Repository rules:

- One PR or issue comment per learning proposal.
- Store candidate skills before promotion.
- Keep full cases in bug libraries, not in domain skills.
- Keep dependency and lifecycle metadata in shared files if the repository mirror exists.
- Use labels: `skill-learning`, `skill-candidate`, `bug-library`, `abstraction`, `lifecycle`, `meta-skill`.
- Promote a candidate only after real use or strong repeated evidence.

If the user plans to create a separate GitHub-comment skill, do not create the repository mirror automatically. Produce GitHub-ready structured summaries and wait for the GitHub-comment skill to publish them.

## Required Confirmation Rule

Before creating, updating, splitting, merging, or deprecating any skill, always present the proposed change and wait for explicit user approval.

If the user proposes a direction but a better structure is available, recommend the better structure, explain the tradeoff, and ask for approval before execution.

## Output

For no learning action:

```yaml
skill_learning_review:
  outcome: "do_not_record"
  reason: ""
```

For a learning action:

```yaml
skill_learning_review:
  outcome: "create_new_skill"
  proposal: {}
  requires_user_confirmation: true
```

## Prohibitions

- Do not create skills from a single weak case.
- Do not confuse bug records with skills.
- Do not create broad vague skills with no workflow.
- Do not update files without explicit confirmation.
- Do not duplicate governance responsibilities.
- Do not store private data, credentials, or proprietary samples in learning records.
