import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC

RUN = Path("results/run7_2018_2021")
DATA = Path("data/processed")
OUT = Path("results/error_analysis.md")
THRESHOLD = 0.6
SAMPLES = 20


def main() -> None:
    train = pd.read_csv(DATA / "train.csv", dtype=str)
    test = pd.read_csv(DATA / "test.csv", dtype=str)
    labels = json.loads((RUN / "labels.json").read_text())
    anomaly_labels, problem_labels = labels["anomaly"], labels["primary_problem"]
    npz = np.load(RUN / "test_predictions.npz", allow_pickle=True)
    y_true = npz["anomaly_true"]
    t_pred = (npz["anomaly_probs"] >= THRESHOLD).astype(int)

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit(train["text"])
    parse = lambda s: [p.strip() for p in s.split(";") if p.strip()]
    y_train = np.array([[int(l in parse(a)) for l in anomaly_labels] for a in train["anomaly"]])
    svm = OneVsRestClassifier(LinearSVC(class_weight="balanced")).fit(vec.transform(train["text"]), y_train)
    b_pred = svm.predict(vec.transform(test["text"]))

    rows = []
    for i, name in enumerate(anomaly_labels):
        rows.append({
            "label": name,
            "support": int(y_true[:, i].sum()),
            "transformer": f1_score(y_true[:, i], t_pred[:, i], zero_division=0),
            "baseline": f1_score(y_true[:, i], b_pred[:, i], zero_division=0),
        })
    per_label = pd.DataFrame(rows).sort_values("support", ascending=False)
    per_label["diff"] = per_label["transformer"] - per_label["baseline"]

    lengths = test["text"].str.split().str.len().to_numpy()
    bins = pd.qcut(lengths, 4, duplicates="drop")
    exact_t = (t_pred == y_true).all(axis=1)
    exact_b = (b_pred == y_true).all(axis=1)
    by_len = pd.DataFrame({"len": bins, "transformer": exact_t, "baseline": exact_b}).groupby("len", observed=True).mean()
    per_row_f1 = lambda p: np.array([f1_score(t, q, zero_division=0) for t, q in zip(y_true, p)])
    over_5 = lengths > 512 * 0.75

    p_true, p_pred = npz["problem_true"], npz["problem_pred"]
    valid = p_true >= 0
    cm = confusion_matrix(p_true[valid], p_pred[valid], labels=range(len(problem_labels)))
    off = cm.copy()
    np.fill_diagonal(off, 0)
    pairs = sorted(((off[i, j], problem_labels[i], problem_labels[j]) for i in range(len(off)) for j in range(len(off)) if off[i, j]), reverse=True)[:10]

    n_pred = t_pred.sum(axis=1)
    n_true = y_true.sum(axis=1)
    rng = np.random.default_rng(0)
    wrong = np.flatnonzero(~exact_t)
    picks = rng.choice(wrong, size=SAMPLES, replace=False)

    out = ["# Error analysis (run 7, test set)\n"]
    out.append(f"Exact-match accuracy over all anomaly labels: transformer {exact_t.mean():.3f}, baseline {exact_b.mean():.3f}\n")
    out.append(f"Labels per report: true mean {n_true.mean():.2f}, transformer predicts {n_pred.mean():.2f}\n")
    out.append("## Per-label F1 (sorted by test support)\n")
    out.append(per_label.round(3).to_markdown(index=False))
    out.append("\n## Exact-match by report length (words, quartiles)\n")
    out.append(by_len.round(3).to_markdown())
    out.append(f"\nReports likely over the 512-token limit (>{int(512 * 0.75)} words): {over_5.mean():.1%} of test\n")
    out.append("## Most common Primary Problem confusions (true -> predicted)\n")
    out += [f"- {n}x  {a} -> {b}" for n, a, b in pairs]
    out.append(f"\n## {SAMPLES} random misclassified reports\n")
    for i in picks:
        true = [anomaly_labels[j] for j in np.flatnonzero(y_true[i])]
        pred = [anomaly_labels[j] for j in np.flatnonzero(t_pred[i])]
        out.append(f"### acn {test['acn'][i]} ({lengths[i]} words)\n- true: {true}\n- predicted: {pred}\n- text: {test['text'][i][:700]}\n")
    OUT.write_text("\n".join(out))
    print(per_label.round(3).head(15).to_string(index=False))
    print(by_len.round(3))
    print(f"over limit {over_5.mean():.1%}; exact t {exact_t.mean():.3f} b {exact_b.mean():.3f}; labels/report true {n_true.mean():.2f} pred {n_pred.mean():.2f}")
    print("better:", per_label.nlargest(5, "diff")[["label", "support", "diff"]].to_string(index=False))
    print("worse:", per_label.nsmallest(5, "diff")[["label", "support", "diff"]].to_string(index=False))
    print("confusions:", *pairs[:6], sep="\n")


if __name__ == "__main__":
    main()
