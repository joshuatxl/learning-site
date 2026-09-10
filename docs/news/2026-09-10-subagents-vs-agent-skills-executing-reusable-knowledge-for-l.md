---
date: '2026-09-10'
fetched: '2026-09-10'
preview: 'How can language model agents effectively leverage libraries of reusable
  knowledge to solve long-horizon tasks? Recent work has increasingly focused on agent
  skills: reusable capabilities represented as skill packages, i.e., multi-file bundles
  containing…'
published: '2026-09-10T04:00:00+00:00'
source: arXiv cs.AI
title: 'Subagents vs Agent Skills: Executing Reusable Knowledge for Long-Horizon Agentic
  Tasks'
url: https://arxiv.org/abs/2609.09233
---

# Subagents vs Agent Skills: Executing Reusable Knowledge for Long-Horizon Agentic Tasks

<p>How can language model agents effectively leverage libraries of reusable knowledge to solve long-horizon tasks? Recent work has increasingly focused on agent skills: reusable capabilities represented as skill packages, i.e., multi-file bundles containing instructions, scripts, and other resources that help agents perform specific tasks. Agent skills are typically executed by loading their skill instructions into an agent&amp;#39;s context and relying on the agent to follow them. As task horizons grow, however, this approach becomes increasingly brittle, because reasoning quality degrades as more information accumulates in the context window. We investigate an alternative approach in which skill packages are instead invoked as subagents. Rather than loading skill instructions into the main context, subagent execution spawns fresh context windows dedicated to solving individual subtasks. We show that subagent execution outperforms agent-skill execution when skill packages expose clear input-output contracts and their instructions encode the procedural knowledge needed to fulfill those contracts. The tradeoff is additional communication overhead, as extra tokens are required to coordinate between the main agent and its subagents. Our results show that the benefit of reusable knowledge depends not only on its content, but also on how it is organized and invoked.</p>

[Read the full article →](https://arxiv.org/abs/2609.09233)