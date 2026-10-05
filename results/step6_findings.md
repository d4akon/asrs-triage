# Step 6: trend analysis, 2018-2021 (21,633 reports, 48 months)

Claims are about *reports received by ASRS*, not about incidents. ASRS is voluntary, so changes in report counts or topics can reflect reporting behaviour, not safety.

## Method
- **Label trends** (`scripts/trends.py`): TF-IDF + linear SVM, 5-fold out-of-fold predictions, so each report is scored by a model that never saw it. Monthly share of reports per anomaly label, from predictions and from the true labels. Change points with PELT on the standardised monthly series.
- **Topic trends** (`scripts/topics.py`): BERTopic (MiniLM sentence embeddings, UMAP, HDBSCAN, reduced to 25 topics; 27% of reports left as outliers). Monthly share per topic. Unsupervised, so it does not depend on analyst labels.

## Findings
1. **Predicted monthly shares track the true ones for specific labels** (correlation 0.89-0.99 for ATC Issue, CFTT/CFIT, NMAC, Smoke/Fire) **but not for generic ones** (Clearance 0.21, FAR 0.42, Published Material 0.59). Median over 53 labels: 0.65. Trend claims are only made for the first group.
2. **A change in coding practice appears at the end of 2020.** Mean labels per report is about 2.5 through 2018-2020, then rises to about 3.2-3.4 from February 2021 (`labels_per_report.png`). The rise comes from FAR, Published Material / Policy, Clearance and Aircraft Equipment Problem Critical. This is almost certainly analysts assigning more labels, not a change in what pilots reported. Share-of-reports trends for these labels across the 2020/2021 boundary should not be read as real-world change. I did not find documentation of the change on the ASRS site (one web search; not exhaustive), so it stays a hypothesis.
3. **The model does not follow that shift, even though 2021 reports are in its training folds.** It misses the 2021 increase because the same text gets different labels before and after the shift (Clearance true +0.075, predicted -0.036 between the first and last 12 months; Aircraft Equipment Problem Critical true +0.155, predicted +0.064). Predicted changes are therefore lower bounds on label-level change. Direction and timing are usable for specific labels, magnitudes are not.
4. **Shared change points** (true and predicted series agree): ATC Issue and Weather/Turbulence step down in 2019-04, Aircraft Equipment Problem Less Severe steps down in 2020-02, NMAC and Aircraft Equipment Problem Critical step up in 2021-05. None has a documented external cause that I could find. The 2021-05 steps overlap with the coding shift above.
5. **COVID-19 is clearly visible, and is the cleanest result.** Report volume falls to 244 in April 2020 (about 450 average) and peaks at 617 in July 2020. BERTopic found an unsupervised topic about masks and mask policy (`mask, passenger, wearing, face, policy`) with 0% of reports until February 2020, 2.6% in March 2020, a peak of 14.7% in August 2020, and under 1% from May 2021. No label in the ASRS taxonomy captures this, so the topic model finds something the supervised labels cannot. Other recent topics are UAS/drone objects (+1.3 points) and hazmat/cargo (+1.3), and the largest decline is a large approach/traffic/altitude topic (-3.9 points).

## Limits
- Only 2018-2021. Four years cannot separate seasonality from trend: no season repeats more than four times.
- Months have 244-687 reports, so monthly shares of rare labels are noisy.
- Out-of-fold folds are random, not chronological, so they mix years in training. A model trained only on the past and applied to the future would likely track drift worse than this analysis suggests.
- The change-point penalty is a judgement call; points were not tuned, but different penalties give different counts.
- External-event matching is limited to COVID-19, which matches. Other points are reported without causes.

## Files
`results/trends/` (summary CSV, monthly shares, `top_label_trends.png`, `labels_per_report.png`, `reports_per_month.png`), `results/topics/` (`topics.csv`, monthly shares, `topic_trends.png`).
