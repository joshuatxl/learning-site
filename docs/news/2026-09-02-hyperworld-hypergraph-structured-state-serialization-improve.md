---
date: 2026-09-02
fetched: '2026-09-02'
preview: World models enable language-model agents to predict environment dynamics
  and plan before acting. In text environments, the model must learn symbolic action
  effects from serialized state descriptions, but the role of serialization structure
  remains…
published: '2026-09-02T00:00:00+00:00'
source: ''
title: 'HyperWorld: Hypergraph-Structured State Serialization Improves Learned Textual
  World Models'
url: https://arxiv.org/abs/2609.00002
---

# HyperWorld: Hypergraph-Structured State Serialization Improves Learned Textual World Models

<p>World models enable language-model agents to predict environment dynamics and plan before acting. In text environments, the model must learn symbolic action effects from serialized state descriptions, but the role of serialization structure remains underexplored. We present HyperWorld, a controlled study of state serialization for learned textual world models. We compare raw observations with three symbolic serializations of the same ground-truth state: independent sentences, pairwise triples, and entity-centered hyperedge units that group multiple related facts around entities and relations. All variants use the same training objective: given a state and an action, predict symbolic effects or judge the action infeasible. Across model scales, data budgets, and in-distribution and out-of-distribution test worlds, hyperedge serialization gives the clearest gains for 0.5B--1.5B models and under distribution shift. Larger models reduce the gap, and pairwise triples can match or slightly exceed hyperedges on in-distribution exact match, but hyperedges achieve the strongest out-of-distribution fact F1 and the best small-to-medium scale trade-off between feasibility detection and effect prediction. In downstream greedy planning, the hyperedge world model also attains the highest success rate among the tested representations. These results show that higher-order state organization is a simple but effective inductive bias for learned symbolic world models, especially when model capacity is limited or test environments differ from training.</p>

[Read the full article →](https://arxiv.org/abs/2609.00002)
