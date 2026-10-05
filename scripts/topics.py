from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP

DATA = Path("data/processed/asrs_clean.csv")
OUT = Path("results/topics")
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
NR_TOPICS = 25
PLOTTED = 6


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA, dtype=str)
    text = df["text"].str.replace("[ANON]", " ", regex=False)

    encoder = SentenceTransformer(ENCODER)
    encoder.max_seq_length = 256
    embeddings = encoder.encode(text.tolist(), batch_size=64, show_progress_bar=True)

    model = BERTopic(
        embedding_model=encoder,
        umap_model=UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=0),
        vectorizer_model=CountVectorizer(stop_words="english", ngram_range=(1, 2), min_df=10),
        min_topic_size=60,
        nr_topics=NR_TOPICS,
    )
    topics, _ = model.fit_transform(text.tolist(), embeddings)
    df["topic"] = topics

    info = model.get_topic_info()
    info["top_words"] = info["Topic"].map(lambda t: ", ".join(w for w, _ in model.get_topic(t)[:8]) if t != -1 else "")
    info[["Topic", "Count", "top_words"]].to_csv(OUT / "topics.csv", index=False)

    share = pd.crosstab(df["date"], df["topic"], normalize="index")
    share.to_csv(OUT / "monthly_topic_share.csv")
    x = [pd.Timestamp(year=int(d[:4]), month=int(d[4:]), day=1) for d in share.index]

    real = [t for t in share.columns if t != -1]
    change = {t: share[t].iloc[-12:].mean() - share[t].iloc[:12].mean() for t in real}
    top = sorted(real, key=lambda t: abs(change[t]), reverse=True)[:PLOTTED]

    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex=True)
    for ax, t in zip(axes.flat, top):
        ax.plot(x, share[t], color="tab:blue")
        ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-05-31"), color="orange", alpha=0.15)
        words = ", ".join(w for w, _ in model.get_topic(t)[:4])
        ax.set_title(f"Topic {t}: {words}", fontsize=9)
        ax.set_ylabel("share of reports")
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(axis="x", labelsize=8)
    fig.suptitle("Topics with the largest change between 2018 and 2021 (orange: spring 2020)")
    fig.tight_layout()
    fig.savefig(OUT / "topic_trends.png", dpi=150)

    pd.set_option("display.width", 200, "display.max_colwidth", 90)
    print(f"outliers (topic -1): {(df['topic'] == -1).mean():.1%}")
    print(info[["Topic", "Count", "top_words"]].to_string(index=False))
    print("largest change first-12 vs last-12 months:")
    for t in top:
        print(f"  topic {t}: {change[t]:+.3f}  ({', '.join(w for w, _ in model.get_topic(t)[:5])})")
    print("by-month check, topic share variance explained by month (std of monthly share):")
    print(share[real].std().round(3).sort_values(ascending=False).head(5).to_string())


if __name__ == "__main__":
    main()
