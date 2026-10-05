# Supervisor summary: automated classification and trend analysis of ASRS reports

## What was built
A pipeline from raw NASA ASRS exports to trained models and a working demo, on 21,633 reports (January 2018 to December 2021). Two prediction targets: **Anomaly** (multi-label, 53 labels with at least 30 training examples) and **Primary Problem** (single label, 18 classes). The Synopsis and Callback fields are never used as input, to avoid label leakage. The split is chronological by month (70/15/15%), not random.

Two models share one evaluation function: a TF-IDF + linear SVM baseline, and DeBERTa-v3-base fine-tuned with LoRA on a free Kaggle GPU (one shared encoder, two heads, class-weighted losses, decision threshold tuned on validation).

A demo runs locally: a FastAPI service serving the baseline and an Angular client with a text area, example reports and a scores panel.

## Main results (test set, 3,027 reports)

| Task | Metric | TF-IDF + SVM | DeBERTa-v3 + LoRA |
|---|---|---|---|
| Anomaly | macro-F1 | **0.401** | 0.376 |
| Anomaly | micro-F1 | **0.603** | 0.522 |
| Primary Problem | macro-F1 | **0.305** | 0.296 |
| Primary Problem | micro-F1 | **0.639** | 0.602 |

1. **The transformer did not beat the baseline.** This contradicts the plan's hypothesis (Section 1). The gap is small on macro-F1 and larger on micro-F1. One run per model and no seeds, so differences under about 0.02 are not established.
2. **More data helped the transformer a lot.** On 2019 alone, Primary Problem macro-F1 was 0.216; with 2018-2021 it is 0.296.
3. **Error analysis.** Exact-match across all labels is 7.5% (transformer) and 12.4% (baseline). The transformer under-predicts (2.6 labels per report against 3.1 true). Accuracy falls with report length, and about 24% of reports likely exceed the 512-token limit. The main Primary Problem confusion is Procedure against Human Factors. Many sampled errors look like analyst label choice, not model failure.

## Trend analysis (Step 6)
Out-of-fold predictions for all reports, monthly label shares, change-point detection, and BERTopic as an unsupervised check.

- Predicted monthly shares follow the true ones well for specific labels (correlation 0.89-0.99: ATC Issue, CFTT/CFIT, NMAC, Smoke/Fire) and poorly for generic ones (Clearance 0.21, FAR 0.42). Trend claims are limited to the first group.
- **COVID-19 is visible.** Report volume drops to 244 in April 2020 and rises to 617 in July 2020. An unsupervised topic about masks goes from 0% of reports to 14.7% in August 2020 and back below 1% by mid-2021. No ASRS label captures this.
- **A coding-practice shift is visible.** Labels per report rise from about 2.5 to 3.2-3.4 from February 2021, driven by FAR, Published Material, Clearance and Equipment Problem Critical. This is likely an analyst effect, not a real change, and means share trends across 2020/2021 for those labels are unreliable. I found no documentation of it (one search); it is a hypothesis.
- Several step changes (ATC Issue and Weather in April 2019, Equipment Less Severe in February 2020, NMAC in May 2021) have no cause I could identify.
- All statements concern reports received, not incidents.

## Limits
- Only four years (about 21.6k reports), below the plan's 30k floor, so seasonality cannot be separated from trend.
- Single training runs; no ablations done yet (truncation, sequence length, learning rate, long-context model).
- Cross-validation for the trend analysis mixes years, so it understates how badly a past-trained model tracks future drift.
- The demo's scores are squashed SVM margins, not calibrated probabilities.

## Scope decisions
- **Demo:** local only, started with `./run_demo.sh`.
- **Emphasis:** research (baseline against transformer, error analysis, trends) and engineering (the demo).
- **Not done, by choice:** ablations, more years of data, a long-context model, ATC speech, hosting. Each is a clear next step and would take about 2.5 GPU hours per transformer run, or manual exports for more data.

## Where everything is
Code and results in the repository `asrs-triage`; tables in `results/tables.md`; full analyses in `results/error_analysis.md` and `results/step6_findings.md`; figures in `results/trends/` and `results/topics/`.
