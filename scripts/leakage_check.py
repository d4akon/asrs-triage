import json
from pathlib import Path

import numpy as np
import pandas as pd
from baseline import parse_labels
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

DATA = Path("data/processed")
LABELS = Path("results/run7_2018_2021/labels.json")
TRENDS = Path("results/trends")
OUT = Path("results/trends_forward")
# Expanding window: each block is predicted by a model trained only on strictly earlier months.
BLOCKS = [("2019", ["2018"]), ("2020", ["2018", "2019"]), ("2021", ["2018", "2019", "2020"])]


def check_split() -> list[str]:
    frames = {n: pd.read_csv(DATA / f"{n}.csv", dtype=str) for n in ("train", "val", "test")}
    lines = []
    for name, df in frames.items():
        lines.append(f"{name}: {df['date'].min()} to {df['date'].max()} ({len(df)} reports)")
    train, val, test = frames["train"], frames["val"], frames["test"]
    lines.append(f"train ends before val starts: {train['date'].max() < val['date'].min()} "
                 f"(share a month: {bool(set(train['date']) & set(val['date']))})")
    lines.append(f"val ends before test starts: {val['date'].max() < test['date'].min()} "
                 f"(share a month: {bool(set(val['date']) & set(test['date']))})")
    for a, b in (("train", "val"), ("train", "test"), ("val", "test")):
        lines.append(f"{a}/{b} shared ACNs: {len(set(frames[a]['acn']) & set(frames[b]['acn']))}, "
                     f"shared identical texts: {len(set(frames[a]['text']) & set(frames[b]['text']))}")
    return lines


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = ["# Leakage check", "", "## Train / validation / test split", ""]
    report += [f"- {line}" for line in check_split()]

    df = pd.read_csv(DATA / "asrs_clean.csv", dtype=str)
    kept = json.loads(LABELS.read_text())["anomaly"]
    binarizer = MultiLabelBinarizer(classes=kept).fit([kept])
    y = binarizer.transform([[l for l in parse_labels(a) if l in kept] for a in df["anomaly"]])
    year = df["date"].str[:4]

    pred = np.full(y.shape, np.nan)
    for test_year, train_years in BLOCKS:
        train_mask, test_mask = year.isin(train_years).to_numpy(), (year == test_year).to_numpy()
        model = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
            OneVsRestClassifier(LinearSVC(class_weight="balanced")),
        ).fit(df.loc[train_mask, "text"], y[train_mask])
        pred[test_mask] = model.predict(df.loc[test_mask, "text"])

    covered = ~np.isnan(pred[:, 0])
    months = df["date"][covered]
    true_share = pd.DataFrame(y[covered], columns=kept).groupby(months.values).mean()
    forward = pd.DataFrame(pred[covered], columns=kept).groupby(months.values).mean()
    forward.to_csv(OUT / "monthly_predicted_share_forward.csv")
    random_cv = pd.read_csv(TRENDS / "monthly_predicted_share.csv", index_col=0, dtype={0: str}).loc[true_share.index]
    summary = pd.read_csv(TRENDS / "label_trend_summary.csv")

    rows = []
    for label in kept:
        t, f, r = true_share[label].to_numpy(), forward[label].to_numpy(), random_cv[label].to_numpy()
        rows.append({
            "label": label,
            "mean_share": summary.loc[summary["label"] == label, "mean_share"].iloc[0],
            "corr_random_cv": np.corrcoef(t, r)[0, 1],
            "corr_forward": np.corrcoef(t, f)[0, 1],
            "mae_random_cv": np.abs(t - r).mean(),
            "mae_forward": np.abs(t - f).mean(),
        })
    table = pd.DataFrame(rows).sort_values("mean_share", ascending=False)
    table.to_csv(OUT / "tracking_random_vs_forward.csv", index=False)

    report += ["", "## Monthly-share tracking, 2019-01 to 2021-12 (36 months)", "",
               f"- median correlation, random 5-fold CV (used before): {table['corr_random_cv'].median():.2f}",
               f"- median correlation, forward in time (trained only on earlier years): {table['corr_forward'].median():.2f}",
               f"- median mean absolute error of the monthly share, random CV: {table['mae_random_cv'].median():.4f}",
               f"- median mean absolute error of the monthly share, forward: {table['mae_forward'].median():.4f}", ""]
    main_labels = table.head(12).round(3)
    report.append(main_labels.to_markdown(index=False))
    Path("results/leakage_check.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
