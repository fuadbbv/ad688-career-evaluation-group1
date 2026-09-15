import os, time, requests, pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
H = {"X-API-Key": KEY}
ANALYTIC = ["analyst", "data", "business intelligence", "statistic",
            "operations research", "database", "mathemat"]
PAT = "|".join(ANALYTIC)

def full_count(naics, max_pages=30):
    rows, offset = [], 0
    for _ in range(max_pages):
        r = requests.get(f"{BASE}/jobs/", headers=H,
                         params={"naics": naics, "limit": 500, "offset": offset}, timeout=180)
        r.raise_for_status()
        j = r.json()
        b = j.get("results", [])
        rows.extend(b)
        if not j["meta"].get("has_more") or not b:
            break
        offset += 500
        time.sleep(0.3)
    df = pd.DataFrame(rows)
    if df.empty:
        return 0, 0, 0, 0
    soc = df.get("soc_name", pd.Series(dtype=str)).astype(str).str.lower()
    an = df[soc.str.contains(PAT, na=False)]
    sal = an["annual_salary_min"].notna().sum() if "annual_salary_min" in an else 0
    us = an["state_code"].astype(str).str.strip().ne("").sum() if "state_code" in an else 0
    return len(df), len(an), int(sal), int(us)

print(f"{'naics':10} {'всего':>7} {'аналитич':>9} {'с зарпл':>8} {'в США':>7}")
print("-" * 46)
for code in ["5241", "524", "52", "5415"]:
    t, a, s, u = full_count(code)
    print(f"{code:10} {t:>7} {a:>9} {s:>8} {u:>7}")
