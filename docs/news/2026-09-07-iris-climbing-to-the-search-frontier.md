---
date: 2026-09-07
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: 'We present Iris-mini and Iris-pro, two search agents trained at the 35B-A3B
  and 397B-A17B scales, together with the data pipeline and training recipe behind
  them. Tasks are reverse-constructed from the hyperlink structure of a web corpus:
  we author multi-hop…'
summary: Researchers have introduced Iris-mini and Iris-pro, two search agents trained
  using a multi-hop web data pipeline and an alternating 'SFT-RL climbing' procedure
  optimized against live search. Evaluated with inference-time context management,
  both models achieved the strongest overall results among open-source search agents
  in their parameter classes across benchmarks such as BrowseComp, DeepSearchQA, and
  HLE. The authors plan to publicly release the model weights alongside the complete
  data construction, training, and evaluation recipes.
title: 'Iris: Climbing to the Search Frontier'
url: https://arxiv.org/abs/2609.04304
---

# Iris: Climbing to the Search Frontier

<p>We present Iris-mini and Iris-pro, two search agents trained at the 35B-A3B and 397B-A17B scales, together with the data pipeline and training recipe behind them. Tasks are reverse-constructed from the hyperlink structure of a web corpus: we author multi-hop chains over an entity graph distilled from a seed page and its out-links, rewrite every non-answer entity into a descriptive reference so that no clue can be resolved by string matching, and admit only questions that a reference model fails closed-book yet solves once the supporting evidence is supplied. These questions are then turned into trajectories, which are filtered at both the trajectory and the turn level before SFT. The policy is then optimized by RL against live search, with the reward judge and the observation summarizer served inside the training cluster, and with over-long rollouts interrupted at the request level and resumed from their committed prefix at the next step. We alternate the two stages in a procedure we call SFT-RL climbing, returning the hardest solved and most efficient rollouts of each RL round to the next supervised pass. Because inference-time context management is worth more on these benchmarks than most reported differences between systems, we evaluate every benchmark both with and without it, holding the tool set, the context limit, and the judge fixed. All results come from a single ReAct agent, with no sub-agents and no test-time verification. With management enabled, on BrowseComp, BrowseComp-ZH, DeepSearchQA, and HLE the two models reach $82.2/84.8/86.9/52.3$ and $88.6/85.1/92.9/56.4$, the strongest overall results among open-source search agents in their respective parameter ranges. We plan to release the model weights together with the complete recipe for data construction, training, and evaluation.</p>

[Read the full article →](https://arxiv.org/abs/2609.04304)
