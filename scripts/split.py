from pathlib import Path

import pandas as pd

SRC = Path("data/processed/asrs_clean.csv")
OUT_DIR = Path("data/processed")
TRAIN_SHARE = 0.70
VAL_SHARE = 0.15


def month_cutoffs(df: pd.DataFrame) -> tuple[str, str]:
    counts = df.groupby("date").size().sort_index()
    cumulative = counts.cumsum() / counts.sum()
    train_end = cumulative.index[cumulative >= TRAIN_SHARE][0]
    val_end = cumulative.index[cumulative >= TRAIN_SHARE + VAL_SHARE][0]
    return train_end, val_end


def main() -> None:
    df = pd.read_csv(SRC, dtype=str)
    train_end, val_end = month_cutoffs(df)
    parts = {
        "train": df[df["date"] <= train_end],
        "val": df[(df["date"] > train_end) & (df["date"] <= val_end)],
        "test": df[df["date"] > val_end],
    }
    for name, part in parts.items():
        part.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: {len(part)} rows, {part['date'].min()} to {part['date'].max()}")


if __name__ == "__main__":
    main()
