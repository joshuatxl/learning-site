---
date: 2026-09-09
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: Current evaluation methods for large language models are coarse-grained and
  decoupled from generation, producing generic explanations that fail to provide actionable
  feedback for model improvement. We propose CriticGen, a fine-grained, generation-aware…
summary: Researchers have introduced CriticGen, a generation-aware framework designed
  to provide fine-grained, actionable feedback for evaluating and improving large
  language models. By dynamically creating instance-specific rubrics, CriticGen enables
  models to diagnose flaws and jointly produce scores, explanations, executable suggestions,
  and refined answers. In experiments, the framework achieved strong score correlations
  and successfully improved over 73% of model responses with a 93.28% non-degradation
  rate.
title: 'CriticGen: Generation-Aware Evaluation as Actionable Feedback'
url: https://arxiv.org/abs/2609.05439
---

# CriticGen: Generation-Aware Evaluation as Actionable Feedback

<p>Current evaluation methods for large language models are coarse-grained and decoupled from generation, producing generic explanations that fail to provide actionable feedback for model improvement. We propose CriticGen, a fine-grained, generation-aware evaluation framework that turns evaluation into actionable control for answer improvement. CriticGen first generates sample-specific evaluation dimensions and scoring criteria under high-level categories such as subjective, objective, and self-derived constraints. These criteria then serve as a dynamic rubric for jointly producing a score, a reason, an executable refinement suggestion, and a refined answer. This rubric-conditioned refinement process enables models to diagnose flaws and perform targeted answer improvement. Experimental results show that fine-grained evaluation should be both instance-specific and actionable. CriticGen induces higher-quality rubrics, improving relevance/coverage from 3.33/4.03 to 3.97/4.24. CriticGen also achieves the best score correlations, with 0.9556 Pearson and 0.9560 Spearman, and raises the F1 of criterion-grounded reasons and executable suggestions from 0.6369/0.5994 to 0.7554/0.7900. Crucially, its feedback translates into reliable answer improvement, improving 73.17% of answers with a 93.28% non-degradation rate.</p>

[Read the full article →](https://arxiv.org/abs/2609.05439)
