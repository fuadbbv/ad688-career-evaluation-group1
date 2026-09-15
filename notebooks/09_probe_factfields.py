import os, json, requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
HEADERS = {"X-API-Key": KEY}

def sample(endpoint, **params):
    resp = requests.get(f"{BASE}/{endpoint}/", headers=HEADERS,
                        params={**params, "limit": 1, "offset": 0}, timeout=120)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None

row = sample("job-facts", naics="523")
if row is None:
    print("job-facts returned no rows for naics=523")
else:
    print("=== job-facts top-level fields ===")
    for key, value in row.items():
        if key in ("metch_payload", "description", "body"):
            kind = f"dict[{len(value)}]" if isinstance(value, dict) else f"{type(value).__name__}[{len(str(value))} chars]"
            print(f"  {key:26} -> {kind}")
        else:
            print(f"  {key:26} = {str(value)[:70]}")

    payload = row.get("metch_payload")
    if isinstance(payload, dict):
        print(f"\n=== metch_payload keys ({len(payload)}) ===")
        keys = sorted(payload.keys())
        for i in range(0, len(keys), 4):
            print("  " + " | ".join(f"{k:24}" for k in keys[i:i+4]))

    print("\n=== fields matching experience / education / degree ===")
    haystack = {**row, **(payload if isinstance(payload, dict) else {})}
    hits = [k for k in haystack
            if any(t in k.lower() for t in ("exp", "edu", "degree", "min_years", "seniority", "level"))]
    if hits:
        for k in hits:
            print(f"  {k:30} = {str(haystack[k])[:70]}")
    else:
        print("  NONE — experience/education are not separate fields")
