"""Step 3.2 - Clean core variables.

Cleaning logic by Katie Bowles. Plumbing fixed by Fuad Babaiev:
- `rows_before` was used before assignment in the duplicate block
- two competing `main()` definitions, one calling a non-existent `clean_data`
- no entry point, so running the file did nothing
- output moved to data/processed/career_market_panel.csv (Section 4 filename)
- text cleaning now runs before dtype casting, so .str works on plain strings
"""
import numpy as np
import pandas as pd
from datetime import datetime

SRC = "data/interim/jobs_naics523_filtered_20260915.csv.gz"
OUT = "data/processed/career_market_panel.csv"
LOG = "outputs/m2_step32_cleaning_log.md"

DATE_COLS = ["posted_at", "expires_at"]
FLOAT_COLS = ["staffing_confidence", "latitude", "longitude",
              "annual_salary_min", "annual_salary_max",
              "hourly_salary_min", "hourly_salary_max", "experience_years_raw"]
INT_COLS = ["search_relevance_score", "skills_count"]
BOOL_COLS = ["is_staffing_agency"]
CATEGORY_COLS = ["state", "state_code", "remote_status", "employment_type",
                 "soc_code", "occupation_family", "education_level_raw",
                 "cip_code", "job_id", "naics_code", "zip_code",
                 "msa_code", "city_code"]
NUMERIC_CATEGORY = {"zip_code", "naics_code", "msa_code", "cip_code"}
DROP_FOR_PANEL = ["description", "bls", "census", "student_signals", "staffing_evidence"]

report = []


def note(message):
    print(message)
    report.append(message)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    note(f"input rows: {len(df)}")

    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True, format="ISO8601")

    rows_before = len(df)
    df = df.drop_duplicates(subset="job_id").reset_index(drop=True)
    note(f"dropped {rows_before - len(df)} duplicate postings (same job_id)")

    required = ["job_id", "title", "company_name", "posted_at"]
    rows_before = len(df)
    df = df.dropna(subset=required)
    note(f"dropped {rows_before - len(df)} rows missing a required field "
         f"({', '.join(required)})")

    bad_dates = (df["expires_at"] < df["posted_at"]).fillna(False)
    df.loc[bad_dates, "expires_at"] = pd.NaT
    note(f"cleared {int(bad_dates.sum())} expires_at values that preceded posted_at")

    for col in ["title", "company_name", "city", "state", "location_text"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
    df["normalized_title"] = df["title"].astype("string").str.lower().str.strip()

    if "zip_code" in df.columns:
        zip_series = (df["zip_code"].astype("string")
                      .str.replace(r"\.0$", "", regex=True)
                      .str.strip().str.zfill(5))
        df["zip_code"] = zip_series.replace(
            {"00000": pd.NA, "nan": pd.NA, "<NA>": pd.NA})

    if "description" in df.columns:
        desc = df["description"].astype("string")
        desc = desc.str.replace(r"<[^>]+>", " ", regex=True)
        df["description"] = desc.str.replace(r"\s+", " ", regex=True).str.strip()

    in_us = df["latitude"].between(18, 72) & df["longitude"].between(-180, -65)
    out_of_range = (~in_us) & df["latitude"].notna()
    df.loc[~in_us, ["latitude", "longitude"]] = np.nan
    note(f"cleared {int(out_of_range.sum())} latitude/longitude pairs outside US bounds")

    swapped = (df["annual_salary_min"] > df["annual_salary_max"]).fillna(False)
    df.loc[swapped, ["annual_salary_min", "annual_salary_max"]] = (
        df.loc[swapped, ["annual_salary_max", "annual_salary_min"]].values)
    note(f"swapped {int(swapped.sum())} reversed annual salary min/max pairs")

    implausible = ((df["annual_salary_min"] < 10_000) |
                   (df["annual_salary_max"] > 1_000_000)).fillna(False)
    df.loc[implausible, ["annual_salary_min", "annual_salary_max"]] = np.nan
    note(f"cleared {int(implausible.sum())} implausible annual salaries "
         f"(below 10,000 or above 1,000,000)")

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].astype("boolean")
    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    for col in FLOAT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    for col in CATEGORY_COLS:
        if col not in df.columns:
            continue
        if col in NUMERIC_CATEGORY and pd.api.types.is_numeric_dtype(df[col]):
            numeric = pd.to_numeric(df[col], errors="coerce")
            df[col] = numeric.map(
                lambda x: pd.NA if pd.isna(x) else str(int(x))).astype("string")
        else:
            series = df[col].astype("string").str.replace(
                r"^(-?\d+)\.0$", r"\1", regex=True)
            df[col] = series.replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
        df[col] = df[col].astype("category")

    typed = set(DATE_COLS + BOOL_COLS + INT_COLS + FLOAT_COLS + CATEGORY_COLS)
    for col in [c for c in df.columns if c not in typed]:
        df[col] = df[col].astype("string")

    note(f"final row count: {len(df)}")
    return df


def main():
    source = pd.read_csv(SRC, compression="gzip", low_memory=False)
    df = clean(source)

    panel = df.drop(columns=[c for c in DROP_FOR_PANEL if c in df.columns])
    panel.to_csv(OUT, index=False)
    note(f"analytical panel written to {OUT}: {len(panel)} rows, {len(panel.columns)} columns")
    note("columns excluded from the panel (full posting text and nested blobs): "
         + ", ".join(c for c in DROP_FOR_PANEL if c in df.columns))

    coverage = {
        "annual salary present": int(panel["annual_salary_min"].notna().sum()),
        "hourly salary present": int(panel["hourly_salary_min"].notna().sum()),
        "state_code present": int(panel["state_code"].notna().sum()),
        "remote_status known": int((panel["remote_status"] != "unknown").sum()),
        "experience_years_raw present": int(panel["experience_years_raw"].notna().sum()),
        "education_level_raw present": int(panel["education_level_raw"].notna().sum()),
    }

    lines = ["# Step 3.2 - Cleaning Core Variables", "",
             f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
             f"Source: `{SRC}`", f"Output: `{OUT}`", "",
             "## Cleaning actions", ""]
    lines += [f"- {m}" for m in report]
    lines += ["", "## Field coverage after cleaning", "",
              "| Field | Rows populated | Share |", "|---|---|---|"]
    for label, count in coverage.items():
        lines.append(f"| {label} | {count} | {count / len(panel):.0%} |")
    with open(LOG, "w") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"\nlog written to {LOG}")


if __name__ == "__main__":
    main()
