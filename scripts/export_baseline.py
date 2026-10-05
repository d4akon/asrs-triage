import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from baseline import MIN_TRAIN_EXAMPLES, parse_labels
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

DATA = Path("data/processed")
OUT = Path("models/baseline")
RESULTS = Path("results")
BINS = 10


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def expected_calibration_error(confidence: np.ndarray, correct: np.ndarray) -> float:
    edges = np.linspace(0, 1, BINS + 1)
    bucket = np.clip(np.digitize(confidence, edges[1:-1]), 0, BINS - 1)
    error = 0.0
    for b in range(BINS):
        mask = bucket == b
        if mask.any():
            error += mask.mean() * abs(confidence[mask].mean() - correct[mask].mean())
    return float(error)


def binarize(frame: pd.DataFrame, binarizer: MultiLabelBinarizer, kept: list[str]) -> np.ndarray:
    labels = frame["anomaly"].map(parse_labels)
    return binarizer.transform([[l for l in row if l in kept] for row in labels])


def fit_anomaly_calibrators(margins: np.ndarray, targets: np.ndarray) -> list:
    # Platt scaling per label; None keeps the plain sigmoid when validation has no positives.
    calibrators = []
    for i in range(targets.shape[1]):
        if targets[:, i].sum() < 5:
            calibrators.append(None)
            continue
        calibrators.append(LogisticRegression(C=100).fit(margins[:, [i]], targets[:, i]))
    return calibrators


def calibrated_anomaly(margins: np.ndarray, calibrators: list) -> np.ndarray:
    out = sigmoid(margins)
    for i, cal in enumerate(calibrators):
        if cal is not None:
            out[:, i] = cal.predict_proba(margins[:, [i]])[:, 1]
    return out


def main() -> None:
    train, val, test = (pd.read_csv(DATA / f"{n}.csv", dtype=str) for n in ("train", "val", "test"))
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    features = vectorizer.fit_transform(train["text"])

    label_lists = train["anomaly"].map(parse_labels)
    counts = pd.Series([l for labels in label_lists for l in labels]).value_counts()
    kept = sorted(counts[counts >= MIN_TRAIN_EXAMPLES].index)
    binarizer = MultiLabelBinarizer(classes=kept).fit([kept])
    anomaly = OneVsRestClassifier(LinearSVC(class_weight="balanced")).fit(features, binarize(train, binarizer, kept))

    known = train["primary_problem"].notna().to_numpy()
    problem = LinearSVC(class_weight="balanced").fit(features[known], train.loc[known, "primary_problem"])

    # Calibration is fitted on validation, reported on test; the SVMs never see either.
    val_x, test_x = vectorizer.transform(val["text"]), vectorizer.transform(test["text"])
    val_margins, test_margins = anomaly.decision_function(val_x), anomaly.decision_function(test_x)
    anomaly_calibrators = fit_anomaly_calibrators(val_margins, binarize(val, binarizer, kept))

    val_known, test_known = val["primary_problem"].notna().to_numpy(), test["primary_problem"].notna().to_numpy()
    problem_calibrator = LogisticRegression(C=10, max_iter=2000).fit(
        problem.decision_function(val_x[val_known]), val.loc[val_known, "primary_problem"]
    )

    y_test = binarize(test, binarizer, kept)
    raw, cal = sigmoid(test_margins), calibrated_anomaly(test_margins, anomaly_calibrators)
    p_margins = problem.decision_function(test_x[test_known])
    p_true = test.loc[test_known, "primary_problem"].to_numpy()
    raw_p = np.exp(p_margins - p_margins.max(axis=1, keepdims=True))
    raw_p /= raw_p.sum(axis=1, keepdims=True)
    cal_p = problem_calibrator.predict_proba(p_margins)
    classes = problem.classes_

    def top_class(p):
        return p.max(axis=1), classes[p.argmax(axis=1)] == p_true

    report = {
        "anomaly": {
            "ece_before": expected_calibration_error(raw.ravel(), y_test.ravel().astype(float)),
            "ece_after": expected_calibration_error(cal.ravel(), y_test.ravel().astype(float)),
            "brier_before": float(np.mean([brier_score_loss(y_test[:, i], raw[:, i]) for i in range(len(kept))])),
            "brier_after": float(np.mean([brier_score_loss(y_test[:, i], cal[:, i]) for i in range(len(kept))])),
        },
        "primary_problem": {
            "ece_before": expected_calibration_error(*top_class(raw_p)),
            "ece_after": expected_calibration_error(*top_class(cal_p)),
            "log_loss_before": float(log_loss(p_true, raw_p, labels=list(classes))),
            "log_loss_after": float(log_loss(p_true, cal_p, labels=list(classes))),
        },
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "calibration.json").write_text(json.dumps(report, indent=2))

    # Retrieval corpus for "similar past reports": every cleaned report, scored with the same vectorizer.
    corpus = pd.read_csv(DATA / "asrs_clean.csv", dtype=str)
    corpus_x = vectorizer.transform(corpus["text"]).tocsr()
    meta = [
        {
            "acn": r.acn,
            "date": r.date,
            "anomaly": parse_labels(r.anomaly),
            "primary_problem": None if pd.isna(r.primary_problem) else r.primary_problem,
            "snippet": r.text[:320],
        }
        for r in corpus.itertuples()
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "vectorizer": vectorizer,
            "anomaly": anomaly,
            "anomaly_labels": kept,
            "problem": problem,
            "anomaly_calibrators": anomaly_calibrators,
            "problem_calibrator": problem_calibrator,
            "corpus_features": corpus_x,
            "corpus_meta": meta,
        },
        OUT / "model.joblib",
    )
    print(f"wrote {OUT / 'model.joblib'} ({len(kept)} anomaly labels, {len(classes)} problem classes, {len(meta)} corpus reports)")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
