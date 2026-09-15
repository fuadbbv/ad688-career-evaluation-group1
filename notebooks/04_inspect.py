import os, glob, json, requests, pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
H = {"X-API-Key": KEY}
pd.set_option("display.width", 160)

path = sorted(glob.glob("data/raw/jobs_naics5221_*.json"))[-1]
df = pd.DataFrame(json.load(open(path)))
print("file:", path, "| rows:", len(df))

for col in ["naics_code", "naics_name", "soc_name", "occupation_family"]:
    print(f"\n=== {col} ===")
    print(df[col].astype(str).value_counts().head(15))

r = requests.get(f"{BASE}/facets/", headers=H, timeout=120)
print("\n\n=== FACETS (без фильтров) status:", r.status_code)
if r.ok:
    for g, items in r.json().get("facets", {}).items():
        print(f"\n## {g}  (всего {len(items)})")
        for it in items[:20]:
            print(f"   {str(it.get('value'))[:28]:30} {str(it.get('label'))[:38]:40} {it.get('count')}")
else:
    print(r.text[:400])
