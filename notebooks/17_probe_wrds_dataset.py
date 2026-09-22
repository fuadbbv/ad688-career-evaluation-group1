"""Probe the Module 3 WRDS jobs dataset: how much of it matches our scope?"""
import glob
import pandas as pd

PARTS = sorted(glob.glob("data/raw/m3_dataset/jobs_2026_part_*.parquet"))
COLS = ["ID", "POSTED", "TITLE_NAME", "TITLE_CLEAN", "COMPANY_NAME",
        "NAICS3", "NAICS3_NAME", "NAICS4", "NAICS4_NAME",
        "SOC_2021_4_NAME", "MIN_YEARS_EXPERIENCE", "MIN_EDULEVELS_NAME",
        "SALARY", "SALARY_FROM", "SALARY_TO", "REMOTE_TYPE_NAME",
        "STATE_NAME", "CITY_NAME", "SKILLS_NAME", "SOFTWARE_SKILLS_NAME",
        "IS_INTERNSHIP"]

frames = []
for i, part in enumerate(PARTS, 1):
    frames.append(pd.read_parquet(part, columns=COLS))
    print(f"  read {i}/{len(PARTS)}: {part.split('/')[-1]}", flush=True)
df = pd.concat(frames, ignore_index=True)
print(f"\ntotal rows: {len(df):,}")

naics3 = df["NAICS3"].astype(str).str.replace(r"\.0$", "", regex=True)
securities = df[naics3 == "523"]
print(f"NAICS 523 rows: {len(securities):,}")
print("\n=== NAICS3 top values overall ===")
print(naics3.value_counts().head(10))

ROLE_SOC = ("data scientist|database architect|statistician|mathematician|"
            "operations research|market research analyst|"
            "financial and investment analyst|credit analyst|management analyst")
ROLE_TITLE = (r"\banalyst\b|\banalytics\b|\bdata\b|business intelligence|\bbi\b|"
              r"reporting|\bsql\b|data scien|machine learning")

soc = securities["SOC_2021_4_NAME"].astype(str).str.lower()
title = securities["TITLE_NAME"].astype(str).str.lower()
role = securities[(soc.str.contains(ROLE_SOC, na=False, regex=True) |
                   title.str.contains(ROLE_TITLE, na=False, regex=True)) &
                  ~soc.str.contains("information security", na=False)]
print(f"\nNAICS 523 + our role filter: {len(role):,} postings")

print("\n=== field coverage in that slice ===")
for col in ["MIN_YEARS_EXPERIENCE", "MIN_EDULEVELS_NAME", "SALARY",
            "SALARY_FROM", "REMOTE_TYPE_NAME", "STATE_NAME",
            "SKILLS_NAME", "SOFTWARE_SKILLS_NAME", "POSTED"]:
    filled = role[col].notna().sum()
    print(f"  {col:22} {filled:>6,}  ({filled/max(len(role),1):.0%})")

print("\n=== top occupations ===")
print(role["SOC_2021_4_NAME"].value_counts().head(10))
print("\n=== posting dates ===")
dates = pd.to_datetime(role["POSTED"], errors="coerce")
print(f"{dates.min()}  ->  {dates.max()}")

role.to_parquet("data/interim/wrds_naics523_role_probe.parquet", index=False)
print(f"\nsaved slice to data/interim/wrds_naics523_role_probe.parquet")
