---
date: 2026-09-07
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: This technical report presents EXAONE Forecast for Finance (EXAONE Finance),
  a financial time series foundation model (TSFM) tailored to financial forecasting.
  While recent TSFMs achieve strong zero-shot performance through large-scale pretraining,
  they are…
summary: '**EXAONE Forecast for Finance** is a new time series foundation model specifically
  designed to address the computational and missing-data challenges inherent to financial
  forecasting. By replacing heavy self-attention mechanisms with efficient linear-time
  operators and pretraining on a massive multi-asset dataset, the model effectively
  captures complex market dynamics. Consequently, EXAONE Finance achieved state-of-the-art
  performance on the FinVerse benchmark, ranking first in point-forecast accuracy,
  cross-sectional asset ranking, and portfolio profitability.'
title: EXAONE Forecast for Finance
url: https://arxiv.org/abs/2609.04239
---

# EXAONE Forecast for Finance

<p>This technical report presents EXAONE Forecast for Finance (EXAONE Finance), a financial time series foundation model (TSFM) tailored to financial forecasting. While recent TSFMs achieve strong zero-shot performance through large-scale pretraining, they are primarily developed for general-domain time series and largely rely on self-attention backbones whose computational cost grows quadratically with sequence length and variate count. Moreover, they assume fully observed inputs and are pretrained on corpora that fail to adequately capture the unique dynamics of financial markets. These limitations hinder their applicability to finance, where long, many-channel, intermittently observed panels are common. To address these challenges, EXAONE Finance adopts an attention-free architecture, replacing self-attention with two simple yet effective linear-time operators: (1) a causal 1D convolution for temporal mixing and (2) a group-aware pooling multi-layer perceptron (MLP) for variate mixing. Furthermore, a masked-context augmentation exposes the model to contiguous missing spans during training, improving robustness to the missingness pervasive in financial markets. EXAONE Finance is pretrained on a synthetic financial corpus whose generative process is designed to reproduce the properties of financial series such as heavy tails, volatility clustering, jumps, regime shifts, and cross-asset dependence, combined with a domain-agnostic synthetic source. On FinVerse, a financial forecasting benchmark covering diverse asset classes, EXAONE Finance attains state-of-the-art performance, ranking first across all three evaluation tiers: point-forecast accuracy, cross-sectional asset ranking, and portfolio profitability.</p>

[Read the full article →](https://arxiv.org/abs/2609.04239)
