# GitHub Comment Style

Use this reference when preparing a GitHub issue comment, PR comment, PR description, or commit summary for skill and project synchronization.

## Tone

- Be factual and compact.
- Prefer visible evidence over broad claims.
- Mention privacy and redaction decisions explicitly.
- Avoid raw secrets, full logs, or proprietary data.

## Template

```markdown
## Skill Updates

- Added/updated `<skill-name>`: <one-line purpose>.
- Scope: <what the skill affects>.
- Validation: <scan, lint, dry run, or manual review>.

## Project Updates

- <project/file group>: <what changed>.

## Bug Library / Learning Notes

- <bug-library or meta-skill update>: <what was recorded or proposed>.

## Risk Review

- Safe to upload: <files/categories>.
- Needs caution: <files/categories and reason>.
- Excluded: <files/categories and reason>.

## Next Step

- <single recommended next action>.
```

## Commit Message Pattern

Use imperative mood and a short subject:

```text
Sync skills and project records

- Add/update skill inventory
- Add/update GitHub-ready summaries
- Exclude local secrets and generated sensitive outputs
```

For a focused skill-only change:

```text
Update Codex skill records

- Refresh custom skill inventory
- Add redacted bug-library guidance
- Prepare GitHub sync notes
```
