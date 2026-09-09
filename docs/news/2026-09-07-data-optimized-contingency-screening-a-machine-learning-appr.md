---
date: 2026-09-07
image: /static/browse/0.3.4/images/arxiv-logo-fb.png
preview: Ensuring the security of the power system is essential for stability and
  reliability, especially in the event of disruption. Effective classification of
  contingency in power systems enables proactive decision-making and mitigates large-scale
  breakdowns and…
summary: Researchers have developed a machine learning framework using Random Forest,
  SVM, and KNN algorithms to classify power system contingencies into safe, moderate,
  or severe risk levels to prevent grid failures. By combining these models with pre-processing
  techniques like PCA and SMOTE, Random Forest achieved the highest performance with
  F1 scores up to 0.97, with PCA contributing the most to model accuracy. Ultimately,
  the study highlights machine learning as a scalable and powerful alternative to
  traditional contingency analysis for real-time power system security assessment.
title: 'Data-Optimized Contingency Screening: A Machine Learning Approach to Power
  System Security'
url: https://arxiv.org/abs/2609.04300
---

# Data-Optimized Contingency Screening: A Machine Learning Approach to Power System Security

<p>Ensuring the security of the power system is essential for stability and reliability, especially in the event of disruption. Effective classification of contingency in power systems enables proactive decision-making and mitigates large-scale breakdowns and failures. This study explores the use of machine learning algorithms to classify security levels of contingencies in power systems into safe, moderate or severe classes. For this approach, Newton-Raphson load flow method extracts system data from contingency scenarios, using Overall Performance Index (OPI) as safety measure. For data pre-processing, Synthetic Minority Over-Sampling Technique (SMOTE) and Principal Component Analysis (PCA) is used to address class imbalance and reduce dimensionality, respectively. K-Nearest Neighbours (KNN), Random Forest (RF) and Support Vector Machines (SVM) is trained and evaluated on datasets generated through N-k contingency scenarios for k equal 1, 2, and 3 on IEEE-14 and IEEE-30 bus systems using four hybrid pre-processing configurations: normalized, SMOTE-balanced, PCA-transformed, and a combined SMOTE PCA-transformed. Performance is assessed by precision, recall and F1 score, with priority given to the severe contingency classes. The RF achieved the highest F1 scores of 0.97 in IEEE-30 and 0.86 in IEEE-14, SVM benefits significantly from PCA and improves the accuracy of the classification, while KNN is best suited for SMOTE and PCA conversion. The findings show that PCA contributes more than SMOTE to the overall performance of the model. However, SMOTE improves recall but can introduce false positives and is therefore a compromise of accuracy. This study highlights machine learning as a scalable and powerful alternative to traditional contingency analysis, which improves the assessment of security in real time.</p>

[Read the full article →](https://arxiv.org/abs/2609.04300)
