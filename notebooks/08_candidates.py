import os, time, requests, pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
HEADERS = {"X-API-Key": KEY}

KEEP = ["job_id", "title", "company_name", "state_code", "remote_status",
        "annual_salary_min", "hourly_salary_min", "soc_name",
        "naics_code", "naics_name", "posted_at"]

# Narrow role filter: data/BI analytics only, excludes security and generic consulting
ROLE_SOC = ("data scientist|database architect|statistician|mathematician|"
            "operations research|market research analyst|"
            "financial and investment analyst|credit analyst|management analyst")
EXCLUDE_SOC = "information security"

def pull(naics, max_pages=80):
    rows, offset = [], 0
    for page in range(1, max_pages + 1):
        resp = requests.get(f"{BASE}/jobs/", headers=HEADERS,
                            params={"naics": naics, "limit": 500, "offset": offset},
                            timeout=180)
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("results", [])
        rows.extend({k: rec.get(k) for k in KEEP} for rec in batch)
        if not payload["meta"].get("has_more") or not batch:
            break
        offset += 500
        time.sleep(0.2)
    return pd.DataFrame(rows)

print(f"{'naics':8} {'total':>7} {'role':>7} {'US':>6} {'annual':>7} {'hourly':>7} {'US+pay':>7}  top sub-industry")
print("-" * 120)

for code in ["523", "5231", "5239", "524", "5241"]:
    df = pull(code)
    if df.empty:
        print(f"{code:8} {'0':>7}")
        continue
    soc = df["soc_name"].astype(str).str.lower()
    role = df[soc.str.contains(ROLE_SOC, na=False) & ~soc.str.contains(EXCLUDE_SOC, na=False)].copy()
    in_us = role["state_code"].astype(str).str.strip().ne("")
    annual = role["annual_salary_min"].notna()
    hourly = role["hourly_salary_min"].notna()
    any_pay = annual | hourly
    top = role["naics_name"].astype(str).value_counts().head(1)
    label = f"{top.index[0][:48]} ({top.iloc[0]})" if len(top) else ""
    print(f"{code:8} {len(df):>7} {len(role):>7} {int(in_us.sum()):>6} "
          f"{int(annual.sum()):>7} {int(hourly.sum()):>7} {int((in_us & any_pay).sum()):>7}  {label}")
