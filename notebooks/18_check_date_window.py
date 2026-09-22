import pandas as pd

df = pd.read_parquet("data/interim/wrds_naics523_role_probe.parquet")
posted = pd.to_datetime(df["POSTED"], errors="coerce")
print(f"rows in probe slice: {len(df):,}")
print(f"rows with no POSTED date: {posted.isna().sum():,}")

for cutoff in ["2025-09-01", "2025-01-01", "2024-09-01", "2023-09-01"]:
    subset = df[posted >= cutoff]
    if len(subset) == 0:
        print(f"{cutoff}: 0")
        continue
    salary = subset["SALARY"].notna().mean()
    state = subset["STATE_NAME"].notna().mean()
    experience = subset["MIN_YEARS_EXPERIENCE"].notna().mean()
    remote = subset["REMOTE_TYPE_NAME"].notna().mean()
    print(f"{cutoff}: {len(subset):>6,} postings | "
          f"salary {salary:.0%} | state {state:.0%} | "
          f"experience {experience:.0%} | remote {remote:.0%}")

print("\npostings per year:")
print(posted.dt.year.value_counts().sort_index().to_string())
