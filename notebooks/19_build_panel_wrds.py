"""Module 3 - rebuild the analytical panel on the WRDS jobs_2026 dataset.

Scope and role rules carry over from Module 2 (Fuad Babaiev).
Cleaning rules carry over from Katie Bowles' Module 2 cleaning script:
duplicates, required fields, date logic, whitespace, salary sanity,
HTML stripping and explicit dtypes. Only the column names change.
The latitude/longitude check is dropped because this dataset has no
coordinates; geography is carried by STATE, CITY_NAME and MSA_NAME.
"""
import glob
from datetime import datetime

import numpy as np
import pandas as pd

PARTS = sorted(glob.glob("data/raw/m3_dataset/jobs_2026_part_*.parquet"))
OUT = "data/processed/career_market_panel.csv"
LOG = "outputs/m3_panel_build_log.md"

NAICS3_TARGET = "523"
POSTED_AFTER = "2025-09-01"

KEEP = [
    "ID", "POSTED", "EXPIRED", "DURATION", "URL",
    "TITLE_RAW", "TITLE_NAME", "TITLE_CLEAN",
    "COMPANY_NAME", "COMPANY_IS_STAFFING", "IS_INTERNSHIP",
    "EDUCATION_LEVELS_NAME", "MIN_EDULEVELS_NAME", "MAX_EDULEVELS_NAME",
    "EMPLOYMENT_TYPE_NAME", "MIN_YEARS_EXPERIENCE", "MAX_YEARS_EXPERIENCE",
    "SALARY", "SALARY_FROM", "SALARY_TO", "ORIGINAL_PAY_PERIOD",
    "REMOTE_TYPE_NAME", "LOCATION", "CITY_NAME", "COUNTY_NAME",
    "MSA_NAME", "STATE", "STATE_NAME",
    "NAICS2_NAME", "NAICS3", "NAICS3_NAME", "NAICS4", "NAICS4_NAME",
    "NAICS5_NAME", "NAICS6_NAME",
    "SOC_2021_4", "SOC_2021_4_NAME", "SOC_2021_5_NAME", "ONET_NAME",
    "CIP4_NAME",
    "SKILLS_NAME", "SPECIALIZED_SKILLS_NAME", "COMMON_SKILLS_NAME",
    "SOFTWARE_SKILLS_NAME", "CERTIFICATIONS_NAME",
]

ROLE_SOC = ("data scientist|database architect|statistician|mathematician|"
            "operations research|market research analyst|"
            "financial and investment analyst|credit analyst|management analyst")
ROLE_TITLE = (r"\banalyst\b|\banalytics\b|\bdata\b|business intelligence|\bbi\b|"
              r"reporting|\bsql\b|data scien|machine learning")
EXCLUDE_SOC = "information security"
EXCLUDE_TITLE = r"security analyst|soc analyst"

report = []


def note(message):
    print(message, flush=True)
    report.append(message)


def flatten(value):
    """Skill columns arrive as arrays; store them as a semicolon-separated string."""
    if isinstance(value, (list, tuple, np.ndarray)):
        return "; ".join(str(v) for v in value if v is not None and str(v) != "nan")
    return value


# ---------------------------------------------------------------- load
available = set(pd.read_parquet(PARTS[0]).columns) if False else None
cols = KEEP
frames = []
for index, part in enumerate(PARTS, 1):
    chunk = pd.read_parquet(part, columns=cols)
    naics3 = chunk["NAICS3"].astype(str).str.replace(r"\.0$", "", regex=True)
    frames.append(chunk[naics3 == NAICS3_TARGET])
    print(f"  part {index}/{len(PARTS)} -> kept {len(frames[-1]):,}", flush=True)

df = pd.concat(frames, ignore_index=True)
note(f"postings in NAICS {NAICS3_TARGET}: {len(df):,}")

# -------------------------------------------------------------- filter
soc = df["SOC_2021_4_NAME"].astype(str).str.lower()
title = df["TITLE_NAME"].astype(str).str.lower()
matched = (soc.str.contains(ROLE_SOC, na=False, regex=True) |
           title.str.contains(ROLE_TITLE, na=False, regex=True))
excluded = (soc.str.contains(EXCLUDE_SOC, na=False, regex=True) |
            title.str.contains(EXCLUDE_TITLE, na=False, regex=True))
note(f"matched the role definition: {int(matched.sum()):,}")
note(f"removed as information-security roles: {int((matched & excluded).sum()):,}")
df = df[matched & ~excluded].copy()

df["POSTED"] = pd.to_datetime(df["POSTED"], errors="coerce")
undated = int(df["POSTED"].isna().sum())
in_window = df["POSTED"] >= POSTED_AFTER
note(f"removed for no publication date: {undated:,}")
note(f"removed as published before {POSTED_AFTER}: "
     f"{int((~in_window).sum()) - undated:,}")
df = df[in_window].copy()

# ------------------------------------------------------------- cleaning
rows_before = len(df)
df = df.drop_duplicates(subset="ID").reset_index(drop=True)
note(f"dropped {rows_before - len(df):,} duplicate postings (same ID)")

required = ["ID", "TITLE_NAME", "COMPANY_NAME", "POSTED"]
rows_before = len(df)
df = df.dropna(subset=required)
note(f"dropped {rows_before - len(df):,} rows missing a required field "
     f"({', '.join(required)})")

df["EXPIRED"] = pd.to_datetime(df["EXPIRED"], errors="coerce")
bad_dates = (df["EXPIRED"] < df["POSTED"]).fillna(False)
df.loc[bad_dates, "EXPIRED"] = pd.NaT
note(f"cleared {int(bad_dates.sum()):,} expiry dates that preceded the posting date")

for col in ["TITLE_RAW", "TITLE_NAME", "TITLE_CLEAN", "COMPANY_NAME",
            "CITY_NAME", "STATE_NAME", "LOCATION", "MSA_NAME"]:
    df[col] = df[col].astype("string").str.strip()
df["TITLE_CLEAN"] = df["TITLE_NAME"].astype("string").str.lower().str.strip()

for col in ["SKILLS_NAME", "SPECIALIZED_SKILLS_NAME", "COMMON_SKILLS_NAME",
            "SOFTWARE_SKILLS_NAME", "CERTIFICATIONS_NAME",
            "EDUCATION_LEVELS_NAME"]:
    df[col] = df[col].map(flatten).astype("string")
df["SKILLS_COUNT"] = df["SKILLS_NAME"].fillna("").apply(
    lambda s: len([p for p in s.split(";") if p.strip()]))
df["SOFTWARE_SKILLS_COUNT"] = df["SOFTWARE_SKILLS_NAME"].fillna("").apply(
    lambda s: len([p for p in s.split(";") if p.strip()]))

for col in ["SALARY", "SALARY_FROM", "SALARY_TO",
            "MIN_YEARS_EXPERIENCE", "MAX_YEARS_EXPERIENCE", "DURATION"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

swapped = (df["SALARY_FROM"] > df["SALARY_TO"]).fillna(False)
df.loc[swapped, ["SALARY_FROM", "SALARY_TO"]] = (
    df.loc[swapped, ["SALARY_TO", "SALARY_FROM"]].values)
note(f"swapped {int(swapped.sum()):,} reversed salary min/max pairs")

implausible = ((df["SALARY_FROM"] < 10_000) | (df["SALARY_TO"] > 1_000_000)).fillna(False)
df.loc[implausible, ["SALARY_FROM", "SALARY_TO"]] = np.nan
bad_single = ((df["SALARY"] < 10_000) | (df["SALARY"] > 1_000_000)).fillna(False)
df.loc[bad_single, "SALARY"] = np.nan
note(f"cleared {int(implausible.sum()):,} implausible salary ranges and "
     f"{int(bad_single.sum()):,} implausible single salary values "
     f"(below 10,000 or above 1,000,000)")

for col in ["REMOTE_TYPE_NAME", "EMPLOYMENT_TYPE_NAME", "STATE", "STATE_NAME",
            "SOC_2021_4_NAME", "SOC_2021_5_NAME", "NAICS3_NAME", "NAICS4_NAME",
            "MIN_EDULEVELS_NAME", "MAX_EDULEVELS_NAME", "ORIGINAL_PAY_PERIOD"]:
    df[col] = df[col].astype("string").replace({"nan": pd.NA, "": pd.NA}).astype("category")

for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].map(flatten).astype("string")

note(f"final row count: {len(df):,}")

df.to_csv(OUT, index=False)
note(f"panel written to {OUT}: {len(df):,} rows, {len(df.columns)} columns")

coverage = {
    "salary (any figure)": int(df[["SALARY", "SALARY_FROM"]].notna().any(axis=1).sum()),
    "salary range (from/to)": int(df["SALARY_FROM"].notna().sum()),
    "US state": int(df["STATE_NAME"].notna().sum()),
    "remote type": int(df["REMOTE_TYPE_NAME"].notna().sum()),
    "minimum years of experience": int(df["MIN_YEARS_EXPERIENCE"].notna().sum()),
    "minimum education level": int(df["MIN_EDULEVELS_NAME"].notna().sum()),
    "skills": int(df["SKILLS_NAME"].notna().sum()),
    "software skills": int(df["SOFTWARE_SKILLS_NAME"].notna().sum()),
    "occupation (SOC 2021)": int(df["SOC_2021_4_NAME"].notna().sum()),
}

lines = ["# Module 3 - Analytical Panel Build", "",
         f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
         "Source: WRDS jobs_2026 dataset (504,208 postings, 134 columns)",
         f"Scope: NAICS {NAICS3_TARGET}, postings from {POSTED_AFTER} onward",
         f"Output: `{OUT}`", "",
         "## Build steps", ""]
lines += [f"- {m}" for m in report]
lines += ["", "## Field coverage", "", "| Field | Populated | Share |", "|---|---|---|"]
for label, count in coverage.items():
    lines.append(f"| {label} | {count:,} | {count / len(df):.0%} |")
with open(LOG, "w") as handle:
    handle.write("\n".join(lines) + "\n")
print(f"\nlog written to {LOG}")
print("\ncolumns:", list(df.columns))
