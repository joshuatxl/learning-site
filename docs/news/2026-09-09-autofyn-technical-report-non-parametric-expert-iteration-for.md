---
date: 2026-09-09
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: We introduce AutoFyn, an agent harness inspired by the Expert Iteration algorithm,
  adapting a frozen model across many rounds by updating persistent state from verified
  reward signals rather than model weights. Each round begins from a fresh model session…
summary: '**AutoFyn** introduces a novel agent framework that enhances frozen AI models
  over long-horizon tasks by updating persistent state—such as memory files and reports—rather
  than modifying model weights. The system employs an orchestrator to explore multiple
  solutions and a verifier to score progress, distilling verified feedback back into
  the durable state to guide subsequent rounds. Demonstrated across mathematics, data
  science, and cybersecurity, AutoFyn outperformed default coding agents on IMO problems,
  topped the Spider 2.0 benchmark, and discovered 16 maintainer-confirmed software
  vulnerabilities.'
title: 'AutoFyn Technical Report: Non-Parametric Expert Iteration for Long-Horizon
  Agents'
url: https://arxiv.org/abs/2609.05446
---

# AutoFyn Technical Report: Non-Parametric Expert Iteration for Long-Horizon Agents

<p>We introduce AutoFyn, an agent harness inspired by the Expert Iteration algorithm, adapting a frozen model across many rounds by updating persistent state from verified reward signals rather than model weights. Each round begins from a fresh model session, and durable information is reintroduced only through explicit interfaces such as persistent memory files, reports, and repository state. Within a round, an orchestrator explores, plans and builds many alternative approaches with specialized agents, while a task-grounded verifier verifies the work and supplies an objective reward for measuring progress. This reward is distilled back into the persistent state, which updates the effective policy for the next round. In this technical report, we formalize this loop and describe its persistent state and verification interfaces. We then demonstrate its use in three domains, namely olympiad mathematics, data science, and cybersecurity. On the six fresh problems of the 2026 International Mathematical Olympiad, every model with room to improve scores higher under AutoFyn than in its provider&amp;#39;s own coding agent. AutoFyn also built the top-ranked agent on the Spider 2.0 dbt benchmark, and has produced $16$ maintainer-confirmed vulnerability advisories in this http URL , MetaMask, pnpm, Warp, LiteLLM, Langflow, and Open WebUI.</p>

[Read the full article →](https://arxiv.org/abs/2609.05446)
