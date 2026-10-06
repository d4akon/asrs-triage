# Supervisor summary: automated classification and trend analysis of ASRS reports

## What was built
A pipeline from raw NASA ASRS exports to trained models and a working demo, on 21,633 reports (January 2018 to December 2021). Two prediction targets: **Anomaly** (multi-label, 53 labels with at least 30 training examples) and **Primary Problem** (single label, 18 classes). The Synopsis and Callback fields are never used as input, to avoid label leakage. The split is chronological by month (70/15/15%), not random.

Two models share one evaluation function: a TF-IDF + linear SVM baseline, and DeBERTa-v3-base fine-tuned with LoRA on a free Kaggle GPU (one shared encoder, two heads, class-weighted losses, decision threshold tuned on validation).

A demo runs locally: a FastAPI service serving the baseline and an Angular client. It classifies a pasted report with calibrated probabilities, shows the words behind each score and the most similar past reports, and has a Trends page with the label and topic time series.

## Main results (test set, 3,027 reports)

| Task | Metric | TF-IDF + SVM | DeBERTa-v3 + LoRA (head truncation) | DeBERTa-v3 + LoRA (head+tail) |
|---|---|---|---|---|
| Anomaly | macro-F1 | **0.401** | 0.376 | 0.396 |
| Anomaly | micro-F1 | **0.603** | 0.522 | 0.513 |
| Primary Problem | macro-F1 | 0.305 | 0.296 | **0.343** |
| Primary Problem | micro-F1 | **0.639** | 0.602 | 0.626 |

1. **The transformer does not clearly beat the baseline, but a truncation fix closes most of the gap.** With the first 510 tokens only (run 7) the baseline won everywhere. Keeping the first 128 and last 382 tokens (run 8) raised Anomaly macro-F1 from 0.376 to 0.396 and Primary Problem macro-F1 from 0.296 to 0.343, now above the baseline on the latter. The baseline stays ahead on micro-F1, so the transformer's gain is on rarer classes. One run per model and no seeds, so differences under about 0.02 are not established. Anomaly threshold tuned on validation was 0.7; at a fixed 0.5 the head+tail model reaches 0.425 on test, reported for transparency but not used as the headline since it was not chosen in advance.
2. **More data helped the transformer a lot.** On 2019 alone, Primary Problem macro-F1 was 0.216; with 2018-2021 it is 0.296 (head truncation) and 0.343 (head+tail).
3. **Error analysis (run 7, before head+tail).** Exact-match across all labels is 7.5% (transformer) and 12.4% (baseline). The transformer under-predicts (2.6 labels per report against 3.1 true). Accuracy falls with report length, and about 24% of reports likely exceed the 512-token limit. The main Primary Problem confusion is Procedure against Human Factors. Many sampled errors look like analyst label choice, not model failure.

## Trend analysis (Step 6)
Out-of-fold predictions for all reports, monthly label shares, change-point detection, and BERTopic as an unsupervised check.

- Predicted monthly shares follow the true ones well for specific labels (correlation 0.89-0.99: ATC Issue, CFTT/CFIT, NMAC, Smoke/Fire) and poorly for generic ones (Clearance 0.21, FAR 0.42). Trend claims are limited to the first group.
- **COVID-19 is visible.** Report volume drops to 244 in April 2020 and rises to 617 in July 2020. An unsupervised topic about masks goes from 0% of reports to 14.7% in August 2020 and back below 1% by mid-2021. No ASRS label captures this.
- **A coding-practice shift is visible.** Labels per report rise from about 2.5 to 3.2-3.4 from February 2021, driven by FAR, Published Material, Clearance and Equipment Problem Critical. This is likely an analyst effect, not a real change, and means share trends across 2020/2021 for those labels are unreliable. I found no documentation of it (one search); it is a hypothesis.
- Several step changes (ATC Issue and Weather in April 2019, Equipment Less Severe in February 2020, NMAC in May 2021) have no cause I could identify.
- All statements concern reports received, not incidents.

## Limits
- Only four years (about 21.6k reports), below the plan's 30k floor, so seasonality cannot be separated from trend.
- Single training runs. One ablation done (truncation); sequence length, learning rate and a long-context model are not.
- Cross-validation for the trend analysis mixes years, so it understates how badly a past-trained model tracks future drift.
- Demo scores are calibrated on the validation split (expected calibration error 0.016 and 0.019 on test), but the cause shown first is the model's decision, which can have a lower probability than another cause.

## Scope decisions
- **Demo:** local only, started with `./run_demo.sh`.
- **Emphasis:** research (baseline against transformer, error analysis, trends) and engineering (the demo).
- **Not done, by choice:** further ablations, more years of data, a long-context model, ATC speech, hosting. Each is a clear next step and would take about 2.5 GPU hours per transformer run, or manual exports for more data.

## Where everything is
Code and results in the repository `asrs-triage`; tables in `results/tables.md`; full analyses in `results/error_analysis.md` and `results/step6_findings.md`; figures in `results/trends/` and `results/topics/`.
