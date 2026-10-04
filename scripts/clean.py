from pathlib import Path

import pandas as pd

SRC = Path("data/processed/asrs_combined.csv")
DST = Path("data/processed/asrs_clean.csv")
MIN_MONTH_RECORDS = 20


def build_text(row: pd.Series) -> str:
    parts = [row["Narrative"], row["Narrative.1"]]
    return " ".join(p.strip() for p in parts if isinstance(p, str) and p.strip())


def main() -> None:
    df = pd.read_csv(SRC, dtype=str)
    text = df.apply(build_text, axis=1).str.replace(r"\bZZZ\w*\b", "[ANON]", regex=True)
    out = pd.DataFrame(
        {
            "acn": df["ACN"],
            "date": df["Date"],
            "text": text,
            "anomaly": df["Anomaly"],
            "primary_problem": df["Primary Problem"],
            "flight_phase": df["Flight Phase"],
        }
    )
    keep = (out["text"].str.len() > 0) & out["anomaly"].notna() & out["date"].notna()
    out = out[keep]
    month_size = out["date"].map(out["date"].value_counts())
    stray = month_size < MIN_MONTH_RECORDS
    print(f"dropping {int(stray.sum())} records from sparse months: {sorted(out.loc[stray, 'date'].unique())}")
    out = out[~stray].reset_index(drop=True)
    out.to_csv(DST, index=False)
    print(f"{len(df)} -> {len(out)} rows, wrote {DST}")


if __name__ == "__main__":
    main()
