---
title: "Long-Horizon State Tracking in LLMs: Executing MD5 through a Deep Sequence of Dependent Tool Calls"
url: "https://arxiv.org/abs/2609.00012"
date: 2026-09-02
---

# Long-Horizon State Tracking in LLMs: Executing MD5 through a Deep Sequence of Dependent Tool Calls

A recent study investigates why large language models (LLMs) struggle with long-horizon tasks, where minor per-step errors typically accumulate and cause total task failure. To cleanly isolate state-tracking performance from instruction interpretation, researchers tasked an LLM with manually computing an MD5 cryptographic hash through a deep sequence of 196 dependent tool calls. The open-weights model `gpt-oss-120b` successfully maintained the 32-bit intermediate state across all steps and produced the exact correct hash in a majority of completed runs. This level of precision was sustained even in a multi-LLM setup operating without exact-arithmetic software, relying instead on context retention and majority voting to fix computational slips. The key takeaway is that LLMs are capable of precise, long-horizon state tracking without inevitable error decay, provided their reasoning is preserved in context and voting mechanisms are applied to eliminate step-level mistakes.

[Read the full article →](https://arxiv.org/abs/2609.00012)
