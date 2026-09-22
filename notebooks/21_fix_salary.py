"""Rebuild the salary fields in the panel with period-aware validation.

SALARY is a text summary column and mostly an empty placeholder, so the
structured figures in SALARY_FROM / SALARY_TO are the only usable source.
Ranges are validated against the pay period they were quoted in; hourly and
monthly rates are kept in their own columns rather than converted to annual,
because the conversion needs an assumption about hours that postings do not make.
"""
import glob

import numpy as np
import pandas as pd

PARTS = sorted(glob.glob("data/raw/m3_dataset/jobs_2026_part_*.parquet"))
PANEL = "data/processed/career_market_panel.csv"

BOUNDS = {"annual": (10_000, 1_000_000),
          "hourly": (5, 500),
          "monthly": (1_000, 100_000)}

frames = []
for part in PARTS:
    chunk = pd.read_parquet(part, columns=["ID", "NAICS3", "ORIGINAL_PAY_PERIOD",
                                           "SALARY_FROM", "SALARY_TO"])
    naics3 = chunk["NAICS3"].astype(str).str.replace(r"\.0$", "", regex=True)
    frames.append(chunk[naics3 == "523"])
raw = pd.concat(frames, ignore_index=True)

panel = pd.read_csv(PANEL, low_memory=False)
raw = raw[raw["ID"].isin(panel["ID"])].drop_duplicates(subset="ID")
print(f"panel rows: {len(panel):,} | matched raw rows: {len(raw):,}")

raw["period"] = raw["ORIGINAL_PAY_PERIOD"].astype("string").str.lower().str.strip()
for col in ["SALARY_FROM", "SALARY_TO"]:
    values = pd.to_numeric(raw[col], errors="coerce")
    raw[col] = values.where(values > 0)

print("\npay period distribution among rows with a figure:")
print(raw.loc[raw["SALARY_FROM"].notna(), "period"].value_counts(dropna=False))

valid = pd.Series(False, index=raw.index)
for period, (low, high) in BOUNDS.items():
    mask = raw["period"] == period
    inside = raw["SALARY_FROM"].between(low, high) & raw["SALARY_TO"].between(low, high)
    valid |= mask & inside
    dropped = int((mask & raw["SALARY_FROM"].notna() & ~inside).sum())
    print(f"  {period:8} kept {int((mask & inside).sum()):>5,}  cleared {dropped:>4,}")

unknown = raw["period"].isna() | ~raw["period"].isin(BOUNDS)
annual_guess = unknown & raw["SALARY_FROM"].between(*BOUNDS["annual"]) & \
               raw["SALARY_TO"].between(*BOUNDS["annual"])
print(f"  unknown period, values in the annual range: {int(annual_guess.sum()):,} "
      f"(treated as annual)")

raw.loc[~(valid | annual_guess), ["SALARY_FROM", "SALARY_TO"]] = np.nan
raw["SALARY_PERIOD"] = raw["period"].where(valid, "annual").where(
    valid | annual_guess, pd.NA)

merged = panel.drop(columns=["SALARY_FROM", "SALARY_TO", "ORIGINAL_PAY_PERIOD"],
                    errors="ignore").merge(
    raw[["ID", "SALARY_FROM", "SALARY_TO", "SALARY_PERIOD"]], on="ID", how="left")

annual = merged["SALARY_PERIOD"] == "annual"
merged["ANNUAL_SALARY_FROM"] = merged["SALARY_FROM"].where(annual)
merged["ANNUAL_SALARY_TO"] = merged["SALARY_TO"].where(annual)
merged["ANNUAL_SALARY_MID"] = merged[["ANNUAL_SALARY_FROM", "ANNUAL_SALARY_TO"]].mean(axis=1)

merged.to_csv(PANEL, index=False)
print(f"\nrewritten {PANEL}: {len(merged):,} rows, {len(merged.columns)} columns")
print(f"any salary figure   : {int(merged['SALARY_FROM'].notna().sum()):,} "
      f"({merged['SALARY_FROM'].notna().mean():.0%})")
print(f"annual salary usable: {int(merged['ANNUAL_SALARY_MID'].notna().sum()):,} "
      f"({merged['ANNUAL_SALARY_MID'].notna().mean():.0%})")
print(f"median annual midpoint: ${merged['ANNUAL_SALARY_MID'].median():,.0f}")
