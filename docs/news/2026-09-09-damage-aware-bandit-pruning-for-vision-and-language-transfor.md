---
date: 2026-09-09
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: Structured post-training pruning of transformers requires selecting complete
  functional units whose suppression causes limited degradation. We formulate structured-unit
  selection for language and vision transformers as a damage-aware multi-armed bandit…
summary: This paper introduces a damage-aware multi-armed bandit framework to improve
  structured post-training pruning for vision and language transformers. By evaluating
  'paired damage' (masked loss minus base loss) on calibration batches, the method
  sequentially identifies and zeroes out attention heads and MLP channels with minimal
  performance loss. Experiments across a wide range of models demonstrate that this
  approach consistently reduces performance degradation compared to traditional pruning
  baselines under a fixed evaluation budget.
title: Damage-Aware Bandit Pruning for Vision and Language Transformers
url: https://arxiv.org/abs/2609.05448
---

# Damage-Aware Bandit Pruning for Vision and Language Transformers

<p>Structured post-training pruning of transformers requires selecting complete functional units whose suppression causes limited degradation. We formulate structured-unit selection for language and vision transformers as a damage-aware multi-armed bandit problem under a fixed candidate-evaluation budget. Attention heads and MLP channel groups are temporarily masked on calibration batches. Paired damage is the masked loss minus the base loss on the same batch, reducing batch-to-batch variation. A smooth bounded reward drives either a UCB-style policy or fractional-Beta Thompson Sampling, and the final mask is constructed sequentially by adding one unit at each step. The selected units are functionally zeroed in the original dense checkpoint; therefore, the reported parameter effects represent effective structural suppression rather than physical compression or measured speedup. Experiments on WikiText-2, LAMBADA, and Imagenette cover GPT-2, OPT, Pythia, Qwen2.5, SmolLM2, ViT-B/16, DeiT-Tiny, and Swin-Tiny, with comparisons against random, magnitude, static-saliency, and budgeted-greedy selection. Across five seeds, the bandit methods usually reduce degradation relative to budgeted greedy in the paired language-model comparisons. Of 28 comparisons highlighted in the paper, 23 bootstrap confidence intervals exclude zero and 11 paired tests have p &amp;lt; 0.05; six have q &amp;lt; 0.05 after Benjamini-Hochberg correction across the full family of 116 dataset-wise tests. Matched-evaluation results for ViT-B/16 and Swin-Tiny indicate that their gains are not explained solely by a larger candidate-evaluation budget.</p>

[Read the full article →](https://arxiv.org/abs/2609.05448)
