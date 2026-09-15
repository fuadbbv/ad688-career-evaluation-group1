import os, time, requests, pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
HEADERS = {"X-API-Key": KEY}

KEEP = ["job_id", "title", "company_name", "state_code", "remote_status",
        "annual_salary_min", "annual_salary_max", "soc_name",
        "occupation_family", "naics_code", "naics_name", "posted_at"]

ANALYTIC = ("analyst|data|business intelligence|statistic|"
            "operations research|database|mathemat")

def pull(naics, max_pages=80):
    """Page through /jobs/ until has_more is false. Keep only needed columns."""
    rows, offset = [], 0
    for page in range(1, max_pages + 1):
        resp = requests.get(f"{BASE}/jobs/", headers=HEADERS,
                            params={"naics": naics, "limit": 500, "offset": offset},
                            timeout=180)
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("results", [])
        rows.extend({k: rec.get(k) for k in KEEP} for rec in batch)
        print(f"  page {page}: +{len(batch)}  total {len(rows)}", flush=True)
        if not payload["meta"].get("has_more") or not batch:
            break
        offset += 500
        time.sleep(0.2)
    return pd.DataFrame(rows)

NAICS = "52"
print(f"Pulling NAICS {NAICS} ...")
df = pull(NAICS)
df.to_csv(f"data/raw/jobs_naics{NAICS}.csv", index=False)

soc = df["soc_name"].astype(str).str.lower()
analytic = df[soc.str.contains(ANALYTIC, na=False)].copy()
analytic["has_salary"] = analytic["annual_salary_min"].notna()
analytic["in_us"] = analytic["state_code"].astype(str).str.strip().ne("")

print(f"\ntotal rows         : {len(df)}")
print(f"analytic roles     : {len(analytic)}")
print(f"  ... in US        : {int(analytic['in_us'].sum())}")
print(f"  ... with salary  : {int(analytic['has_salary'].sum())}")
print(f"  ... US + salary  : {int((analytic['in_us'] & analytic['has_salary']).sum())}")

print("\n=== analytic roles by sub-industry ===")
print(analytic["naics_name"].astype(str).value_counts().head(12))
print("\n=== top SOC ===")
print(analytic["soc_name"].astype(str).value_counts().head(12))
print("\n=== remote status ===")
print(analytic["remote_status"].value_counts())
print("\n=== top states ===")
print(analytic["state_code"].astype(str).value_counts().head(10))
