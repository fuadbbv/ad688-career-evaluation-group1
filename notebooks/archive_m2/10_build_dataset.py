"""Step 3.1 - Build the filtered industry-career dataset.

Industry : NAICS 523 (Securities, Commodity Contracts and Other
           Financial Investments and Related Activities)
Pathway  : Business Intelligence / Data Analyst
Source   : MET Employability Career Match API, /student/jobs/
"""
import os, re, json, time, requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["EMPLOYABILITY_API_KEY"]
BASE = "https://met-employability-services.azurewebsites.net/api/v1/student"
HEADERS = {"X-API-Key": KEY}

NAICS = "523"
POSTED_AFTER = "2025-09-01"      # rolling 12-month window
LIMIT, MAX_PAGES = 500, 80

ROLE_SOC = ("data scientist|database architect|statistician|mathematician|"
            "operations research|market research analyst|"
            "financial and investment analyst|credit analyst|management analyst")
ROLE_TITLE = (r"\banalyst\b|\banalytics\b|\bdata\b|business intelligence|\bbi\b|"
              r"reporting|\bsql\b|data scien|machine learning")
EXCLUDE_SOC = "information security"
EXCLUDE_TITLE = r"security analyst|soc analyst"

EDU_PATTERNS = [
    ("PhD",        r"\bph\.?\s?d\b|doctorate"),
    ("Master",     r"\bmaster'?s?\b|\bm\.?s\.?\b|\bmba\b"),
    ("Bachelor",   r"\bbachelor'?s?\b|\bb\.?s\.?\b|\bb\.?a\.?\b"),
    ("Associate",  r"\bassociate'?s? degree\b"),
    ("HighSchool", r"high school diploma|\bged\b"),
]

def fetch_all():
    rows, offset = [], 0
    for page in range(1, MAX_PAGES + 1):
        resp = requests.get(f"{BASE}/jobs/", headers=HEADERS,
                            params={"naics": NAICS, "posted_after": POSTED_AFTER,
                                    "limit": LIMIT, "offset": offset}, timeout=180)
        resp.raise_for_status()
        payload = resp.json()
        batch = payload.get("results", [])
        rows.extend(batch)
        print(f"  page {page}: +{len(batch)}  total {len(rows)}", flush=True)
        if not payload["meta"].get("has_more") or not batch:
            break
        offset += LIMIT
        time.sleep(0.2)
    return rows

def skills_to_text(value):
    if isinstance(value, list):
        names = [s.get("name") for s in value if isinstance(s, dict) and s.get("name")]
        if not names:
            names = [str(s) for s in value if isinstance(s, str)]
        return "; ".join(names)
    return ""

def extract_experience_years(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"(\d{1,2})\s*(?:\+|plus)?\s*(?:-|–|to)?\s*\d{0,2}\s*\+?\s*year", text, re.I)
    return int(match.group(1)) if match else None

def extract_education(text):
    if not isinstance(text, str):
        return None
    lowered = text.lower()
    for label, pattern in EDU_PATTERNS:
        if re.search(pattern, lowered):
            return label
    return None

# ---------------------------------------------------------------- pull
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/interim", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d")

print(f"Pulling NAICS {NAICS}, posted_after={POSTED_AFTER} ...")
raw = fetch_all()
raw_path = f"data/raw/jobs_naics{NAICS}_raw_{stamp}.json"
with open(raw_path, "w") as handle:
    json.dump(raw, handle)
print(f"raw saved -> {raw_path}")

df = pd.DataFrame(raw)
n_pulled = len(df)

# ------------------------------------------------------------- filter
soc = df["soc_name"].astype(str).str.lower()
title = df["title"].astype(str).str.lower()
keep = ((soc.str.contains(ROLE_SOC, na=False, regex=True)) |
        (title.str.contains(ROLE_TITLE, na=False, regex=True)))
drop = (soc.str.contains(EXCLUDE_SOC, na=False, regex=True) |
        title.str.contains(EXCLUDE_TITLE, na=False, regex=True))
n_role = int(keep.sum())
n_excluded = int((keep & drop).sum())
df = df[keep & ~drop].copy()

# duplicates by job_id
n_before_dedup = len(df)
df = df.drop_duplicates(subset="job_id")
n_dups = n_before_dedup - len(df)

# ------------------------------------------------------- derived cols
df["skills_text"] = df["skills"].apply(skills_to_text)
df["skills_count"] = df["skills_text"].apply(lambda s: len([p for p in s.split(";") if p.strip()]))
df["experience_years_raw"] = df["description"].apply(extract_experience_years)
df["education_level_raw"] = df["description"].apply(extract_education)
df["organization_name"] = df["organization"].apply(
    lambda o: o.get("name") if isinstance(o, dict) else None)
df = df.drop(columns=["skills", "organization"], errors="ignore")

out_path = f"data/interim/jobs_naics{NAICS}_filtered_{stamp}.csv.gz"
df.to_csv(out_path, index=False, compression="gzip")

# ---------------------------------------------------------------- log
lines = [
    "# Step 3.1 - Filtered Industry-Career Dataset",
    "",
    f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
    "",
    "## Scope",
    f"- Industry: NAICS {NAICS} (Securities, Commodity Contracts and Other Financial Investments)",
    "- Career pathway: Business Intelligence / Data Analyst",
    f"- Date window: postings with posted_at >= {POSTED_AFTER}",
    "- Source: MET Employability Career Match API, endpoint `/student/jobs/`",
    "",
    "## Filter funnel",
    f"- Postings pulled for the industry and date window: {n_pulled}",
    f"- Matched the role definition (SOC or title): {n_role}",
    f"- Removed as out-of-scope (information security roles): {n_excluded}",
    f"- Removed as duplicate job_id: {n_dups}",
    f"- **Final analytical dataset: {len(df)} rows**",
    "",
    "## Role definition",
    f"- SOC contains: `{ROLE_SOC}`",
    f"- OR title contains: `{ROLE_TITLE}`",
    f"- Excluded SOC: `{EXCLUDE_SOC}`; excluded title: `{EXCLUDE_TITLE}`",
    "",
    "## Derived columns added in this step",
    "- `skills_text` - skill names flattened to a semicolon-separated string",
    "- `skills_count` - number of skills listed",
    "- `experience_years_raw` - first 'N years' figure found in the description (UNCLEANED)",
    "- `education_level_raw` - highest degree keyword found in the description (UNCLEANED)",
    "- `organization_name` - employer name lifted out of the nested organization object",
    "",
    "## Known data-quality issues to handle in Step 3.2",
    f"- Missing state_code: {int(df['state_code'].astype(str).str.strip().eq('').sum())} of {len(df)}",
    f"- remote_status = unknown: {int((df['remote_status'] == 'unknown').sum())} of {len(df)}",
    f"- Missing annual_salary_min: {int(df['annual_salary_min'].isna().sum())} of {len(df)}",
    f"- Missing hourly_salary_min: {int(df['hourly_salary_min'].isna().sum())} of {len(df)}",
    f"- experience_years_raw not found: {int(df['experience_years_raw'].isna().sum())} of {len(df)}",
    f"- education_level_raw not found: {int(df['education_level_raw'].isna().sum())} of {len(df)}",
    "",
    "## Output",
    f"- `{out_path}` ({len(df)} rows, {len(df.columns)} columns)",
    f"- Raw API response kept locally at `{raw_path}` (git-ignored)",
]
log_path = "outputs/m2_step31_filter_log.md"
with open(log_path, "w") as handle:
    handle.write("\n".join(lines) + "\n")

print("\n".join(lines[8:]))
print(f"\ndataset -> {out_path}")
print(f"log     -> {log_path}")
print("\ncolumns:", list(df.columns))
