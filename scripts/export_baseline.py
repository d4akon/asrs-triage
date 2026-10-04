from pathlib import Path

import joblib
import pandas as pd
from baseline import MIN_TRAIN_EXAMPLES, parse_labels
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

DATA = Path("data/processed")
OUT = Path("models/baseline")


def main() -> None:
    train = pd.read_csv(DATA / "train.csv", dtype=str)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    features = vectorizer.fit_transform(train["text"])

    label_lists = train["anomaly"].map(parse_labels)
    counts = pd.Series([l for labels in label_lists for l in labels]).value_counts()
    kept = sorted(counts[counts >= MIN_TRAIN_EXAMPLES].index)
    binarizer = MultiLabelBinarizer(classes=kept)
    targets = binarizer.fit_transform([[l for l in labels if l in kept] for labels in label_lists])
    anomaly = OneVsRestClassifier(LinearSVC(class_weight="balanced")).fit(features, targets)

    known = train["primary_problem"].notna().to_numpy()
    problem = LinearSVC(class_weight="balanced").fit(features[known], train.loc[known, "primary_problem"])

    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"vectorizer": vectorizer, "anomaly": anomaly, "anomaly_labels": kept, "problem": problem},
        OUT / "model.joblib",
    )
    print(f"wrote {OUT / 'model.joblib'} ({len(kept)} anomaly labels, {len(problem.classes_)} problem classes)")


if __name__ == "__main__":
    main()
