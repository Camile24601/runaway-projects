---
name: github-skill-sync
description: Prepare Codex skill, bug-library, and project changes for safe GitHub synchronization. Use when the user wants to整理 skills, update a GitHub repo, generate commit messages, PR descriptions, issue/PR comments, changelog-style summaries, or review what should be uploaded before approving git add, commit, push, or GitHub comments. Also use proactively after Codex edits project files, SKILL.md files, skill-records, bug-library content, or GitHub-facing docs, so the user can confirm whether to sync the update to GitHub.
---

# GitHub Skill Sync

## Core Principle

Use this skill to make GitHub synchronization semi-automatic and review-first.

Never upload, commit, push, open PRs, or post GitHub comments until the user explicitly approves the exact action. The default output is a GitHub-ready package: upload scope, risk notes, commit message, PR/comment draft, and next commands to run after approval.

## Proactive Trigger

At the end of a task, use this skill proactively when Codex created, edited, or exported any of these:

- `SKILL.md` files.
- `skill-records/`.
- Bug-library records or bug-library skill instructions.
- Project source, README, configuration examples, or GitHub-facing docs.
- Git ignore rules or files that affect upload safety.

When this trigger fires, do not upload automatically. Briefly tell the user that GitHub sync may be appropriate, show the recommended scope or run the summary script, and ask for confirmation before any Git or GitHub write.

## Scope

Scan both:

- The current project workspace.
- User-maintained Codex skills under `~/.codex/skills`, excluding `.system` skills by default.

Treat these as first-class sync candidates:

- Project-local `SKILL.md` files.
- Global user skills such as governance, learning, bug-library, SAP, finance, and other custom skills.
- Bug-library schemas and approved, redacted bug entries.
- Project README, scripts, configs, sample data, and docs.

Treat these as sensitive until reviewed:

- Generated reports from real data.
- Raw traceback, SQL, spreadsheet, or log content that may reveal company data.
- Supabase URLs/keys, tokens, `.env`, credentials, private connection strings.
- Customer, supplier, finance, or personal journal content.

## Workflow

1. Run a read-only scan:

   ```bash
   python3 .codex/skills/github-skill-sync/scripts/scan_skills.py --workspace .
   ```

2. Generate a GitHub-ready summary:

   ```bash
   python3 .codex/skills/github-skill-sync/scripts/build_github_summary.py --workspace .
   ```

3. Dry-run exporting global and workspace skill records into the repository:

   ```bash
   python3 .codex/skills/github-skill-sync/scripts/export_skill_records.py --workspace .
   ```

   Add `--write` only after the user approves creating or refreshing `skill-records/`. The exporter mirrors complete skill folders by default, including `SKILL.md`, `references/`, `assets/`, and `agents/`, while excluding caches, temporary files, and files larger than the exporter limit.

4. Review the output with the user:
   - `upload_recommended`
   - `upload_with_caution`
   - `do_not_upload`
   - `skill_inventory`
   - `bug_library_inventory`
   - `github_commit_message`
   - `github_comment_draft`
   - `approval_required_actions`

5. If the user approves, perform the requested Git action only within the approved scope.

6. After upload, report the exact files committed, remote branch, commit hash, and GitHub URL if available.

## GitHub Comment Style

When generating comments for issues, PRs, or commit discussion, read `references/github-comment-style.md`.

Prefer this structure:

```markdown
## Skill Updates

- ...

## Project Updates

- ...

## Bug Library / Learning Notes

- ...

## Risk Review

- ...

## Next Step

- ...
```

Keep comments factual, concise, and auditable. Do not include secrets or full proprietary data samples.

## Bug Library Policy

Bug libraries are valuable and should usually be versioned in a private GitHub repository after redaction.

Store:

- Bug schema.
- Redacted symptoms.
- Root cause category.
- Fix summary.
- Prevention rule.
- Validation checklist.

Do not store:

- Raw credentials.
- Production connection strings.
- Full proprietary datasets.
- Unredacted customer, supplier, employee, or personal data.
- Full logs when short summaries are enough.

## Coordination With Existing Meta Skills

Use `skill-learning-meta-skill` before this skill when deciding whether a case should become a new skill, an existing skill update, or a bug-library entry.

Use `skill-governance-meta-skill` before editing existing skills when ownership, conflicts, dependencies, drift, or approval proposals are involved.

Use this skill after learning/governance when the user wants the approved or proposed skill knowledge prepared for GitHub.

## External Output Safety Check

Before generating or approving text that may leave the local workspace, run a lightweight input/output safety check.

Applies to:

- GitHub commit messages, PR descriptions, issue/PR comments, release notes, and changelog-style summaries.
- Skill or bug-library excerpts prepared for public or private GitHub repositories.
- Any generated recommendation that includes SAP steps, finance logic, credentials, customer/supplier context, logs, or business data.

Check both:

- Input risk: whether the source material contains secrets, proprietary data, personal data, or operational details that should be redacted.
- Output risk: whether the generated GitHub-facing text leaks sensitive details, overstates safety/quality, includes unsafe instructions, or reveals private workflow context.

If API moderation/safety scores are available, use them as an extra signal. If they are not available, perform the same review manually and label it as a manual safety check. Do not treat a low score or clean check as permission to upload; user approval is still required.

When risk is found, move the item to `upload_with_caution` or `do_not_upload`, propose redacted wording, and explain the reason briefly.

## Approval Boundary

Before any write to Git or GitHub, show:

- Files to include.
- Files to exclude.
- Sensitive findings and redaction decisions.
- Commit message.
- Comment/PR text.
- Exact command class to run, such as `git add`, `git commit`, `git push`, or `gh pr comment`.

Proceed only after explicit user approval.
