# Radar Criteria

Score each candidate from 0-3 on the dimensions below. Recommend only items with either one 3-point signal or at least 7 total points.

## Dimensions

- Recency: published or materially updated in the last 7 days.
- Momentum: sudden stars/forks/releases/discussion, credible community adoption, or notable maintainers.
- Authority: official OpenAI/Anthropic source, primary project docs, recognized research lab, or established maintainer.
- Practical leverage: immediately useful for coding, automation, agent workflows, evaluation, data processing, documents, spreadsheets, presentations, SAP automation, or finance scripts.
- Skill potential: could become a new Codex skill, update an existing skill, or provide a reusable checklist/script/reference.
- Reliability: clear docs, license, tests, examples, active issues, or stable API.
- Novelty: teaches a new concept, architecture, evaluation method, or implementation pattern rather than a shallow wrapper.

## Ranking Heuristics

Promote:

- Official OpenAI/Anthropic updates that change how the user should build or prompt agents.
- Tools that compress repeated local work into a deterministic workflow.
- Repos with fast, credible momentum plus usable docs.
- Concepts that map cleanly to the user's skill-learning loop.

Down-rank:

- Hype-only launches without docs or source.
- Repos with unclear license, unsafe install steps, abandoned maintainers, or no examples.
- Benchmarks without reproducibility.
- Agent frameworks that duplicate existing tooling without a clear advantage.

## Recommendation Levels

- `立刻关注`: strong signal and clear user fit.
- `值得试用`: promising, but needs one small experiment.
- `先收藏`: interesting but not urgent.
- `暂不推荐`: weak signal, risky, duplicated, or unclear.
