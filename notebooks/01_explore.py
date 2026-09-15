import os, json, requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = os.environ.get("EMPLOYABILITY_API_BASE_URL", "").rstrip("/")
PREFIX = os.environ.get("EMPLOYABILITY_API_PATH_PREFIX", "").strip("/")
if PREFIX and not BASE.endswith(PREFIX):
    BASE = f"{BASE}/{PREFIX}"
H = {"X-API-Key": KEY}
print("BASE:", BASE)

def probe(path, **params):
    """Вернуть meta.count и одну строку-образец."""
    r = requests.get(f"{BASE}/{path.strip('/')}/", headers=H,
                     params={**params, "limit": 1, "offset": 0}, timeout=60)
    r.raise_for_status()
    j = r.json()
    return j["meta"]["count"], (j["results"][0] if j["results"] else None)

# --- 1. Сколько всего и сколько в нашей нише
print("\n=== COUNTS ===")
tests = [
    ("всё",                      {}),
    ("naics=5221",               {"naics": "5221"}),
    ("naics=522110",             {"naics": "522110"}),
    ("naics=522",                {"naics": "522"}),
    ("naics=banking",            {"naics": "banking"}),
    ("naics=finance",            {"naics": "finance"}),
    ("q=analyst",                {"q": "analyst"}),
    ("naics=5221 + q=analyst",   {"naics": "5221", "q": "analyst"}),
    ("naics=5221 + q=data",      {"naics": "5221", "q": "data"}),
]
for label, p in tests:
    try:
        n, _ = probe("job-facts", **p)
        print(f"{label:28} -> {n}")
    except Exception as e:
        print(f"{label:28} -> ERROR {e}")

# --- 2. Как выглядит одна строка
print("\n=== SAMPLE ROW FIELDS ===")
n, row = probe("job-facts", q="analyst")
if row:
    for k, v in row.items():
        if k == "metch_payload":
            print(f"  metch_payload -> {len(v) if isinstance(v, dict) else '?'} колонок")
            continue
        s = str(v)
        print(f"  {k:24} = {s[:70]}")
    if isinstance(row.get("metch_payload"), dict):
        print("\n  metch_payload keys:")
        print("   ", ", ".join(list(row["metch_payload"].keys())))

# --- 3. Что вообще есть в отрасли: facets
print("\n=== FACETS (naics=5221) ===")
r = requests.get(f"{BASE}/facets/", headers=H, params={"naics": "5221"}, timeout=60)
if r.ok:
    for group, items in r.json().get("facets", {}).items():
        print(f"\n## {group}")
        for it in items[:12]:
            print(f"   {it.get('label')}  —  {it.get('count')}")
else:
    print(r.status_code, r.text[:300])