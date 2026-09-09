---
date: 2026-09-07
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: Evaluating agents on the growing number of agentic benchmarks is challenging
  because they often require complex environments and agent integrations. We introduce
  Harbor Adapters, a unified evaluation infrastructure for agentic benchmarks. Our
  work makes three…
summary: To simplify agentic evaluation across complex environments, researchers developed
  Harbor Adapters, an open-source infrastructure that adapts over 80 benchmarks for
  testing arbitrary AI agents. Using this platform, the authors conducted a large-scale
  evaluation of eight models across 54 benchmarks and introduced Harbor-Index, a curated
  and affordable meta-dataset of 82 challenging tasks from 29 benchmarks. Across all
  evaluated model-harness configurations on Harbor-Index, no model exceeded a 30%
  pass rate, demonstrating the suite's high difficulty and effectiveness for testing
  agent capabilities.
title: 'Harbor Adapters and Harbor-Index: Infrastructure and a Curated Meta-Dataset
  for Large-Scale Agentic Evaluation'
url: https://arxiv.org/abs/2609.04298
---

# Harbor Adapters and Harbor-Index: Infrastructure and a Curated Meta-Dataset for Large-Scale Agentic Evaluation

<p>Evaluating agents on the growing number of agentic benchmarks is challenging because they often require complex environments and agent integrations. We introduce Harbor Adapters, a unified evaluation infrastructure for agentic benchmarks. Our work makes three contributions. First, we develop benchmark adapters that port more than 80 benchmarks to evaluate arbitrary agents, and validate them through rigorous code review and parity experiments. Second, we conduct a large-scale evaluation of 8 models spanning capability tiers across 54 benchmarks; every model is run with Terminus-2 and with one of 3 native harnesses. This enables a broader analysis of agent capabilities and failure modes than was previously possible. Third, we introduce Harbor-Index, a curated set of 82 difficult, diverse, and high-quality tasks spanning 29 benchmarks, refined from the adapted suite through difficulty filtering, AI and human audit, and an audit-and-fix loop. Harbor-Index preserves the challenge and breadth of large-scale agentic evaluations while being affordable to run; no evaluated model-harness configuration exceeds 30% pass rate, and the strongest (GPT-5.5 with Codex) reaches 28.0%. We release the adapters, evaluation results, in-depth analysis, and Harbor-Index as open-source artifacts to support more reliable and comprehensive evaluation of language-model agents.</p>

[Read the full article →](https://arxiv.org/abs/2609.04298)
