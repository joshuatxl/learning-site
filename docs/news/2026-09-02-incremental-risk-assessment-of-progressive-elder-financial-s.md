---
date: 2026-09-02
fetched: '2026-09-02'
preview: Financial scams targeting older adults increasingly occur through text and
  voice channels such as email, SMS, and phone calls, unfolding over multiple conversational
  turns that begin with impersonation or casual contact, escalate through trust building
  and…
published: '2026-09-02T00:00:00+00:00'
source: ''
title: Incremental Risk Assessment of Progressive Elder Financial Scams via Instruction-Tuned
  Small Language Models
url: https://arxiv.org/abs/2609.00005
---

# Incremental Risk Assessment of Progressive Elder Financial Scams via Instruction-Tuned Small Language Models

<p>Financial scams targeting older adults increasingly occur through text and voice channels such as email, SMS, and phone calls, unfolding over multiple conversational turns that begin with impersonation or casual contact, escalate through trust building and urgency, and culminate in requests for sensitive information or financial transfers. Because risk signals emerge incrementally across turns, effective detection requires models that continuously update risk estimates under resource-constrained deployment settings. We propose a cumulative turn-based risk assessment framework that incrementally aggregates conversational turns and re-estimates risk at each step, enabling dynamic scam monitoring across progressively evolving conversations. A multi-turn dialogue dataset is constructed to cover investment, charity, and tech support scam scenarios, with each dialogue containing two to eight turns and annotated at every cumulative stage with a qualitative risk level, a continuous risk score, an explanatory rationale, and a safety recommendation. Four small language models (Phi-4, LLaMA-3.2, DeepSeek-R1, and Qwen3) are fine-tuned and evaluated under a unified training framework. Fine-tuned small models capture fraud-related linguistic cues and cross-turn escalation patterns while maintaining compact architectures suitable for mobile and resource-constrained deployment settings. Among the evaluated models, Phi-4 and LLaMA-3.2 achieve stronger turn-aware risk estimation performance relative to their parameter scale. These results suggest that structured cumulative modeling can support incremental scam risk assessment in deployment-oriented settings while highlighting the potential of compact language models for privacy-aware and on-device fraud protection.</p>

[Read the full article →](https://arxiv.org/abs/2609.00005)
