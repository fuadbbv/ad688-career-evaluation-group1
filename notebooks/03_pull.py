import os, json, time, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
H = {"X-API-Key": KEY}
LIMIT = 500
MAX_PAGES = 40

def pull(path, params):
    rows, offset, page = [], 0, 0
    while page < MAX_PAGES:
        r = requests.get(f"{BASE}/{path}/", headers=H,
                         params={**params, "limit": LIMIT, "offset": offset}, timeout=90)
        r.raise_for_status()
        j = r.json()
        batch = j.get("results", [])
        rows.extend(batch)
        page += 1
        print(f"  page {page}: +{len(batch)}  total {len(rows)}")
        if not j["meta"].get("has_more") or not batch:
            break
        offset += LIMIT
        time.sleep(0.3)
    return rows

os.makedirs("data/raw", exist_ok=True)
print("Pulling all NAICS 5221 postings...")
rows = pull("jobs", {"naics": "5221"})

stamp = datetime.now().strftime("%Y%m%d")
out = f"data/raw/jobs_naics5221_{stamp}.json"
with open(out, "w") as f:
    json.dump(rows, f)
print(f"\nSaved {len(rows)} rows -> {out}")

import pandas as pd
df = pd.DataFrame(rows)
print("\n=== COLUMNS ===")
print(list(df.columns))
print("\n=== TOP TITLES ===")
print(df["title"].value_counts().head(25))
print("\n=== TOP COMPANIES ===")
print(df["company_name"].value_counts().head(15))
print("\n=== STATES ===")
print(df["state_code"].value_counts().head(12))
print("\n=== REMOTE ===")
print(df["remote_status"].value_counts())
print("\n=== SALARY COVERAGE ===")
print("with salary:", df["annual_salary_min"].notna().sum(), "of", len(df))
