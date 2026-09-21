from pathlib import Path

import pandas as pd

raw_dir = Path("data/raw")

files = sorted(raw_dir.glob("asrs_*.csv"))
dfs: list[pd.DataFrame] = []

for path in files:
  dfs.append(pd.read_csv(path, header=1))

combined = pd.concat(dfs, ignore_index=True)

combined.to_csv("data/processed/asrs_combined.csv", index=False)