# Personal Skills Library

This directory is the version-controlled source library for personal Codex and ChatGPT Skills. The active Codex installation remains under `~/.codex/skills/`.

## Required workflow

1. Search GitHub before creating a Skill.
2. Evaluate matching repositories for documentation, `SKILL.md`, structure, maintenance, adoption, license, dependencies, modifiability, and security risk.
3. Present candidates and wait for approval before installing or modifying anything.
4. Prefer a mature existing Skill, then an adapted close match, and create a new Skill only when no suitable option exists.
5. Validate locally and report the change list before any Git operation.
6. Require explicit approval before `git add`, `git commit`, or `git push`.

Never force-push, use `reset --hard` to overwrite work, or replace local modifications with an upstream update.

## Version policy

Versioned directories such as `v0-1` are immutable releases. Create a new directory for `v0-2` or `v1-0`; do not silently replace the contents of an existing version directory.

For an upstream Skill, record the upstream commit in `SKILLS_INDEX.md`. Before updating, compare the recorded commit, current source, installed copy, and new upstream source. If local changes exist, show the diff and wait for approval.
