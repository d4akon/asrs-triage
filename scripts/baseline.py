import json
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

from evaluate import evaluate

DATA = Path("data/processed")
RESULTS = Path("results")
MIN_TRAIN_EXAMPLES = 30


def parse_labels(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv", dtype=str)


def run_anomaly(train, test, vectorizer):
    train_labels = train["anomaly"].map(parse_labels)
    counts = pd.Series([label for labels in train_labels for label in labels]).value_counts()
    kept = sorted(counts[counts >= MIN_TRAIN_EXAMPLES].index)
    mlb = MultiLabelBinarizer(classes=kept)
    y_train = mlb.fit_transform([[l for l in labels if l in kept] for labels in train_labels])
    y_test = mlb.transform([[l for l in labels if l in kept] for labels in test["anomaly"].map(parse_labels)])
    model = OneVsRestClassifier(LinearSVC(class_weight="balanced"))
    model.fit(vectorizer.transform(train["text"]), y_train)
    y_pred = model.predict(vectorizer.transform(test["text"]))
    return evaluate(y_test, y_pred, kept) | {"n_labels": len(kept)}


def run_primary_problem(train, test, vectorizer):
    train = train.dropna(subset=["primary_problem"])
    test = test.dropna(subset=["primary_problem"])
    classes = sorted(train["primary_problem"].unique())
    model = LinearSVC(class_weight="balanced")
    model.fit(vectorizer.transform(train["text"]), train["primary_problem"])
    y_pred = model.predict(vectorizer.transform(test["text"]))
    return evaluate(test["primary_problem"], y_pred, classes) | {"n_labels": len(classes)}


def main() -> None:
    train, test = load("train"), load("test")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    vectorizer.fit(train["text"])
    results = {
        "anomaly": run_anomaly(train, test, vectorizer),
        "primary_problem": run_primary_problem(train, test, vectorizer),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "baseline.json").write_text(json.dumps(results, indent=2))
    for task, r in results.items():
        print(f"{task}: macro_f1={r['macro_f1']:.3f} micro_f1={r['micro_f1']:.3f} "
              f"hamming={r['hamming_loss']:.3f} labels={r['n_labels']}")


if __name__ == "__main__":
    main()
