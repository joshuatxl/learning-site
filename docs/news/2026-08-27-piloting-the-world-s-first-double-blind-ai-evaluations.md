---
date: '2026-08-27'
fetched: '2026-09-10'
image: https://lh3.googleusercontent.com/fHN8sOK3p7BTKR4s-3lpYYnq5IEadmVKnqssJO4OmfL6remdC7E8voV-IEue8NPviKWUR7WtCtNTfsKZpld6y2jjwVhNAiqYL9-9EQzj5OURGXCCuug=w528-h297-n-nu-rw-lo
preview: Building trust in proprietary model benchmarks using cryptographically secure
  environments Imagine a student is set to take a high-stakes exam. If they accidentally
  peek at the test questions in advance, achieving a perfect score is influenced by
  this…
published: '2026-08-27T12:59:16+00:00'
source: DeepMind
title: Piloting the world's first double-blind AI evaluations
url: https://deepmind.google/blog/piloting-the-worlds-first-double-blind-ai-evaluations/
---

# Piloting the world's first double-blind AI evaluations

<p>Building trust in proprietary model benchmarks using cryptographically secure environments</p><p>Imagine a student is set to take a high-stakes exam. If they accidentally peek at the test questions in advance, achieving a perfect score is influenced by this knowledge, making it a meaningless accomplishment. To truly measure what they know, they must have no visibility of the test questions until it&#x27;s time to take the exam. That is the exact challenge the industry faces when evaluating advanced AI models. If a model has already seen the test questions - a problem known as benchmark contamination - the results can only be trusted to an extent.</p><p>Today, we’re introducing the <strong>world’s first double-blind evaluation of a proprietary, frontier class AI model,</strong> which keeps external evaluations confined to a cryptographic “box” where they can’t be used by models later to optimize performance ahead of testing. We&#x27;re partnering with the Singapore AI Safety Institute, OpenMined, AVERI, and <a href="https://mlcommons.org/2026/08/double-blind-reliability-evaluation/">MLCommons</a>, to test a Gemini Flash Lite model against confidential benchmarks in a <a href="https://cloud.google.com/blog/products/identity-security/verifiable-trust-in-the-ai-era-whats-new-in-confidential-computing">privacy-preserving environment</a>, increasing evaluation integrity.</p><p>At Google, we assess our AI systems using a broad spectrum of evaluations throughout model development and deployment, but we don’t rely on internal testing alone. To identify potential blindspots, we work with a diverse group of external partners, including specialized research labs, civil society and national AI Safety and Security Institutes (AISIs), using their unique expertise to stress-test our models.</p><p>As AI models become more capable, ensuring the model has not seen the test questions or prompts in advance is critical, as this can skew the results. Policymakers, researchers, and enterprises need to trust that AI benchmarks accurately reflect a model&#x27;s true capabilities and safety, but if models are able to “peek” at the evaluation questions in advance, it can artificially inflate scores and undermine this trust.</p><p>Although zero-logging protocols and rigorous contractual safeguards have long kept external test prompts confidential, incorporating technical and cryptographic safeguards marks a major step forward in secure model evaluation.</p><h2>How double-blind evaluations work</h2>

[Read the full article →](https://deepmind.google/blog/piloting-the-worlds-first-double-blind-ai-evaluations/)