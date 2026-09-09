---
date: 2026-09-09
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: Long-term memory for LLM agents is evaluated today by conversational recall
  benchmarks (LoCoMo, LongMemEval), which measure question answering over dialogue
  history, not whether remembered facts change what a tool-using agent does. We present
  MERIT (Memory…
summary: Researchers introduced MERIT, a new benchmark that evaluates how long-term
  memory affects task-executing LLM agents under strict cost and token accounting.
  The study found that using memory dramatically increases task success—raising it
  from a baseline of 0.00 up to 1.00—though swapping memory implementations can alter
  success rates by up to 60 points. Furthermore, update-on-write memory systems significantly
  outperformed embedding retrieval when handling updated facts, while full dialogue
  replay was proven to never be economically viable.
title: When Does Memory Help? A Cost-Aware Evaluation of Long-Term Memory in Tool-Using
  LLM Agents
url: https://arxiv.org/abs/2609.05441
---

# When Does Memory Help? A Cost-Aware Evaluation of Long-Term Memory in Tool-Using LLM Agents

<p>Long-term memory for LLM agents is evaluated today by conversational recall benchmarks (LoCoMo, LongMemEval), which measure question answering over dialogue history, not whether remembered facts change what a tool-using agent does. We present MERIT (Memory Evaluation for Realistic Instrumented Tasks), a benchmark and harness that measures the marginal utility of memory for task-executing agents under explicit cost accounting. MERIT provides episodic tool-use tasks in three domains whose dependence on earlier-episode facts is verified by an automated leak check; a difficulty ladder ending in updated-fact recall; controlled memory corruption; and full token and dollar metering of every memory operation. Across 23,440 scored episodes ($42.57), a two-generation pilot on gpt-4.1-mini and a preregistered 3-model x 3-seed grid (GPT-4.1, Claude Haiku 4.5; memory side held fixed), memory lifts dependent-task success from a leak-verified floor of 0.00 to 0.55-1.00. On updated facts, embedding retrieval collapses unpredictably (0.30-0.95 across models; max seed gap 0.45), and agents act on a correctly retrieved value only 55% of the time, while update-on-write stores (a structured fact store and, notably, LLM summarization) remain at 0.70-1.00; the hybrid is worse than the fact store alone. A latest-generation spot-check (Claude Sonnet 5, gated on a clean full-replay control) reproduces the pattern. Swapping a memory&amp;#39;s implementation moves task success by up to 60 points, and full replay is never economical: the best condition per domain delivers 2.7-3.9x its marginal utility per dollar. We release the benchmark, harness, and all traces.</p>

[Read the full article →](https://arxiv.org/abs/2609.05441)
