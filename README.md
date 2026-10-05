# asrs-triage

Automated classification and trend analysis of aviation safety reports from the NASA Aviation Safety Reporting System (ASRS). Master's thesis proof of concept.

Given the narrative of a report, the system predicts the analyst-assigned **Anomaly** labels (multi-label, 53 labels) and the **Primary Problem** (single label, 18 classes). It also measures how label and topic frequencies change month by month over 2018-2021.

A TF-IDF + linear SVM baseline and a fine-tuned DeBERTa-v3 (LoRA) are compared with the same evaluation code. Results are in `results/`; the baseline is what the demo app serves.

## Results (chronological test split, 3,027 reports)

| Task | Metric | TF-IDF + SVM | DeBERTa-v3 + LoRA |
|---|---|---|---|
| Anomaly | macro-F1 | 0.401 | 0.376 |
| Anomaly | micro-F1 | 0.603 | 0.522 |
| Primary Problem | macro-F1 | 0.305 | 0.296 |
| Primary Problem | micro-F1 | 0.639 | 0.602 |

Details: `results/baseline.json`, `results/run7_2018_2021/`, `results/error_analysis.md`, `results/step6_findings.md`.

Reports are voluntary and unverified. Every finding describes reports received, not incidents that happened.

## Layout

| Path | What |
|---|---|
| `scripts/load_raw.py` | combine the raw ASRS CSV exports |
| `scripts/clean.py` | build one text field, replace `ZZZ` placeholders, drop unusable rows |
| `scripts/split.py` | chronological train/validation/test split by month |
| `scripts/baseline.py`, `scripts/evaluate.py` | baseline and the shared evaluation function |
| `scripts/train_transformer.py`, `scripts/build_kaggle_notebook.py` | GPU training and the Kaggle notebook builder |
| `scripts/error_analysis.py` | transformer vs baseline error analysis |
| `scripts/trends.py`, `scripts/topics.py` | label trends with change points; BERTopic themes |
| `scripts/export_baseline.py` | save the baseline model for the API |
| `api/` | FastAPI prediction service |
| `web/` | Angular client |

## Reproduce

Python 3.12. Raw exports (not in the repo, ASRS terms apply) go in `data/raw/asrs_*.csv`.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/load_raw.py && python scripts/clean.py && python scripts/split.py
python scripts/baseline.py
python scripts/trends.py && python scripts/topics.py
```

The transformer needs a GPU: `python scripts/build_kaggle_notebook.py`, upload `data/kaggle` as a Kaggle dataset, then push the notebook (see `notebooks/kernel-metadata.json`). Training takes a few hours on a free Kaggle GPU.

## Run the demo

```bash
./run_demo.sh
```

Starts the API on port 8000 and the client on port 4200 (open http://localhost:4200); Ctrl+C stops both. It builds the baseline model on first run and runs `npm install` if needed. The API reads `MODEL_PATH` and `ALLOWED_ORIGINS` from the environment. Scores are squashed SVM margins, not calibrated probabilities.

## Limits

Only 2018-2021 is included (about 21.6k reports). Analysts appear to assign more labels per report from 2021, which shifts label shares; see `results/step6_findings.md`.
