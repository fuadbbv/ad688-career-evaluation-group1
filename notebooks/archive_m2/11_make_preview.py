import glob
import pandas as pd

src = sorted(glob.glob("data/interim/jobs_naics523_filtered_*.csv.gz"))[-1]
df = pd.read_csv(src)

PREVIEW_COLS = [
    "job_id", "posted_at", "title", "company_name", "city", "state_code",
    "remote_status", "annual_salary_min", "annual_salary_max",
    "soc_name", "occupation_family", "experience_years_raw",
    "education_level_raw", "skills_count", "skills_text",
]
preview = df[PREVIEW_COLS].head(200)
preview.to_csv("outputs/dataset_preview_200.csv", index=False)

print(f"source : {src}  ({len(df)} rows, {len(df.columns)} cols)")
print("preview: outputs/dataset_preview_200.csv (200 rows)")
print(preview.head(10).to_string())
