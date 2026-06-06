---
name: ai-weekly-radar
description: Run a weekly AI technology radar that scans GitHub, official OpenAI/Anthropic publications, and the user's skill ecosystem for newly useful AI techniques, concepts, tools, and Codex skills; rank signal quality, summarize the essence in Chinese first, and wait for the user to ask before expanding.
---

# AI Weekly Radar

Use this skill when the user asks for a weekly AI technology scan, AI trend radar, GitHub AI project discovery, useful new AI skills, official OpenAI/Anthropic updates, or a Chinese digest of newly useful AI concepts/tools.

## Core Output Rule

Always lead with the most useful distilled insight in Chinese. Do not start with source-by-source notes.

Default response shape:

1. `本周最值得看`: 3-5 items ranked by usefulness.
2. `为什么值得`: one concise reason per item, tied to a signal.
3. `你可能会用在哪`: connect to the user's known skill ecosystem and workflows.
4. `我建议先追哪一个`: one recommendation.
5. `可追问方向`: short prompts the user can choose from.

Keep the first answer compact. Wait for user interest before deep-diving, installing, modifying skills, or creating files.

## Weekly Scan Workflow

1. Set the window to the last 7 days unless the user specifies otherwise.
2. Collect signals from:
   - GitHub trending, new repositories, releases, stars, forks, issues, and discussions.
   - Official OpenAI publications, docs, cookbook updates, model/release notes, and API changes.
   - Official Anthropic news, docs, cookbook/examples, model/release notes, and engineering posts.
   - Trusted primary sources for projects when available: repo README, release notes, docs, paper, changelog.
   - The user's installed skills, especially `skill-learning-meta-skill`, to infer likely usefulness.
3. Prefer primary sources. Browse when recency matters.
4. Score candidates using `references/radar_criteria.md`.
5. Summarize in Chinese using `references/report_format.md`.
6. Clearly label inference when usefulness is inferred from signals rather than proven usage.

## What Counts As Useful

Prioritize items with one or more strong signals:

- Sudden GitHub attention: unusual new stars, forks, watchers, contributors, issues, or adoption by credible users.
- Official release: OpenAI or Anthropic documentation, API behavior, model, cookbook, safety, eval, or agent guidance changed.
- Workflow leverage: could reduce repeated work, prevent bugs, improve automation reliability, or become a Codex skill/reference/script.
- Skill fit: maps to the user's existing skills around finance Excel automation, SAP GUI download automation, bug libraries, document/spreadsheet/presentation generation, or skill governance/learning.
- Conceptual leverage: introduces a reusable technique, evaluation method, agent pattern, prompt strategy, tool architecture, or operational practice.

Do not promote items only because they are flashy. Down-rank thin demos, unsupported benchmarks, vague agent frameworks, dead repos, or projects with risky install/security posture.

## Skill Ecosystem Fit

When judging whether a new skill is worth recommending, use `skill-learning-meta-skill` logic:

- Is there a recognizable trigger condition?
- Does it have stable inputs and outputs?
- Would it reduce repeated prompting, repeated bugs, or repeated decisions?
- Could it become a concise skill, reference, checklist, or script?
- Would adding it make an existing skill clearer rather than bloated?

If yes, propose the smallest next step: try once, save as reference, update existing skill, create new skill, or ignore for now.

## Source Discipline

- Include links for all important claims.
- Compare dates and prefer items published or substantially updated inside the weekly window.
- If using GitHub popularity as a signal, state whether it is a current level or a growth signal.
- Avoid overclaiming benchmarks, model quality, or production readiness from demos.
- Flag security, licensing, maintenance, or dependency risks when obvious.

## References

- Use `references/radar_criteria.md` for scoring and ranking.
- Use `references/report_format.md` for the Chinese output template.
