import os, requests, pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
H = {"X-API-Key": KEY}

ANALYTIC = ["analyst", "data", "business intelligence", "statistic",
            "operations research", "database", "mathemat"]

def probe(**params):
    r = requests.get(f"{BASE}/jobs/", headers=H,
                     params={**params, "limit": 500, "offset": 0}, timeout=120)
    r.raise_for_status()
    j = r.json()
    rows = j.get("results", [])
    more = j["meta"].get("has_more")
    if not rows:
        return 0, more, 0, ""
    df = pd.DataFrame(rows)
    soc = df.get("soc_name", pd.Series(dtype=str)).astype(str).str.lower()
    n_an = int(soc.str.contains("|".join(ANALYTIC), na=False).sum())
    top = df.get("naics_name", pd.Series(dtype=str)).astype(str).value_counts().head(2)
    label = " | ".join(f"{k[:42]}({v})" for k, v in top.items())
    return len(rows), more, n_an, label

cands = ["5221", "5223", "5222", "522", "52", "finance", "insurance", "524", "5241",
         "5112", "software", "5415", "computer systems design", "621", "healthcare"]

print(f"{'naics filter':26} {'rows':>5} {'more':>6} {'analytic':>9}  top naics_name")
print("-" * 110)
for c in cands:
    try:
        n, more, na, lab = probe(naics=c)
        print(f"{c:26} {n:>5} {str(more):>6} {na:>9}  {lab}")
    except Exception as e:
        print(f"{c:26} ERROR {e}")

print("\n\n=== FACETS с q=analyst ===")
r = requests.get(f"{BASE}/facets/", headers=H, params={"q": "analyst"}, timeout=120)
print("status:", r.status_code)
if r.ok:
    for g, items in r.json().get("facets", {}).items():
        print(f"\n## {g}  ({len(items)})")
        for it in items[:15]:
            print(f"   {str(it.get('label'))[:45]:47} {it.get('count')}")
