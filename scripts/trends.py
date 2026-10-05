import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ruptures as rpt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

DATA = Path("data/processed/asrs_clean.csv")
LABELS = Path("results/run7_2018_2021/labels.json")
OUT = Path("results/trends")
PENALTY = 0.5
PLOTTED = 6


def parse_labels(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def month_axis(index: pd.Index) -> list[pd.Timestamp]:
    return [pd.Timestamp(year=int(d[:4]), month=int(d[4:]), day=1) for d in index]


def change_points(series: np.ndarray) -> list[int]:
    # Standardise so one penalty works for rare and common labels alike.
    z = (series - series.mean()) / (series.std() or 1.0)
    ends = rpt.Pelt(model="l2", min_size=4).fit(z.reshape(-1, 1)).predict(pen=PENALTY * np.log(len(z)) * 4)
    return ends[:-1]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA, dtype=str)
    kept = json.loads(LABELS.read_text())["anomaly"]
    mlb = MultiLabelBinarizer(classes=kept)
    mlb.fit([kept])
    parsed = df["anomaly"].map(parse_labels)
    y = mlb.transform([[l for l in labels if l in kept] for labels in parsed])

    # Out-of-fold predictions: every report is scored by a model that never saw it.
    pipeline = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
        OneVsRestClassifier(LinearSVC(class_weight="balanced")),
    )
    pred = cross_val_predict(pipeline, df["text"], y, cv=KFold(5, shuffle=True, random_state=0))

    months = df["date"]
    true_share = pd.DataFrame(y, columns=kept).groupby(months.values).mean()
    pred_share = pd.DataFrame(pred, columns=kept).groupby(months.values).mean()
    counts = months.value_counts().sort_index()
    x = month_axis(true_share.index)
    true_share.to_csv(OUT / "monthly_true_share.csv")
    pred_share.to_csv(OUT / "monthly_predicted_share.csv")

    rows = []
    for label in kept:
        t, p = true_share[label].to_numpy(), pred_share[label].to_numpy()
        rows.append({
            "label": label,
            "mean_share": t.mean(),
            "tracking_corr": np.corrcoef(t, p)[0, 1],
            "bias": (p - t).mean(),
            "true_change": t[-12:].mean() - t[:12].mean(),
            "pred_change": p[-12:].mean() - p[:12].mean(),
            "pred_change_points": [x[i].strftime("%Y-%m") for i in change_points(p)],
            "true_change_points": [x[i].strftime("%Y-%m") for i in change_points(t)],
        })
    summary = pd.DataFrame(rows).sort_values("mean_share", ascending=False)
    summary.to_csv(OUT / "label_trend_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 3))
    ax.bar(x, counts.to_numpy(), width=25)
    ax.set(title="Reports per month in the dataset", ylabel="reports")
    fig.tight_layout()
    fig.savefig(OUT / "reports_per_month.png", dpi=150)
    plt.close(fig)

    per_report = pd.Series(y.sum(axis=1)).groupby(months.values).mean()
    fig, ax = plt.subplots(figsize=(9, 3))
    ax.plot(x, per_report.to_numpy())
    ax.set(title="Mean number of anomaly labels per report", ylabel="labels per report")
    fig.tight_layout()
    fig.savefig(OUT / "labels_per_report.png", dpi=150)
    plt.close(fig)

    top = summary[summary["mean_share"] > 0.03].copy()
    top["abs_change"] = top["pred_change"].abs()
    top = top.nlargest(PLOTTED, "abs_change")
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex=True)
    for ax, label in zip(axes.flat, top["label"]):
        ax.plot(x, true_share[label], label="true labels", color="0.55")
        ax.plot(x, pred_share[label], label="predicted (out-of-fold)", color="tab:blue")
        for i in change_points(pred_share[label].to_numpy()):
            ax.axvline(x[i], color="tab:red", linestyle="--", linewidth=1)
        ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-05-31"), color="orange", alpha=0.15)
        ax.set_title(label, fontsize=9)
        ax.set_ylabel("share of reports")
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(axis="x", labelsize=8)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Monthly share of reports per anomaly label (red: detected change point, orange: spring 2020)")
    fig.tight_layout()
    fig.savefig(OUT / "top_label_trends.png", dpi=150)
    plt.close(fig)

    pd.set_option("display.width", 200, "display.max_colwidth", 60)
    print(f"{len(df)} reports, {len(counts)} months, {counts.min()}-{counts.max()} reports/month")
    print(f"median tracking correlation (predicted vs true monthly share): {summary['tracking_corr'].median():.2f}")
    print(summary[["label", "mean_share", "tracking_corr", "bias", "true_change", "pred_change"]].head(12).round(3).to_string(index=False))
    print(top[["label", "true_change", "pred_change", "pred_change_points", "true_change_points"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
