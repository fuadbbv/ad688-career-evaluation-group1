"""Build the data dictionary for career_market_panel.csv and report
which required field caused rows to be dropped during cleaning."""
import pandas as pd

INTERIM = "data/interim/jobs_naics523_filtered_20260915.csv.gz"
PANEL = "data/processed/career_market_panel.csv"
OUT_CSV = "outputs/data_dictionary.csv"
OUT_MD = "outputs/data_dictionary.md"

DESCRIPTIONS = {
    "job_id": "Unique posting identifier assigned by the MET API; used to deduplicate",
    "posted_at": "Date the posting was published",
    "expires_at": "Date the posting expires; cleared when earlier than posted_at",
    "title": "Job title as published by the employer",
    "normalized_title": "Title lowercased and trimmed, for grouping",
    "company_name": "Employer name as published on the posting",
    "organization_name": "Employer name from the linked organization record",
    "is_staffing_agency": "True when the posting comes from a staffing agency",
    "staffing_confidence": "API confidence score that the poster is a staffing agency",
    "location_text": "Free-text location as published",
    "city": "City parsed from the location",
    "city_code": "Internal city identifier",
    "state": "State name",
    "state_code": "Two-letter US state code; empty for non-US postings",
    "zip_code": "Five-digit ZIP code; 00000 treated as missing",
    "msa_code": "Metropolitan statistical area code",
    "msa_name": "Metropolitan statistical area name",
    "latitude": "Latitude; cleared when outside US bounds",
    "longitude": "Longitude; cleared when outside US bounds",
    "remote_status": "remote, hybrid, onsite or unknown",
    "employment_type": "Full-time, part-time, contract and similar",
    "salary_text": "Raw salary block as returned by the API",
    "annual_salary_min": "Lower bound of the annual salary range in USD",
    "annual_salary_max": "Upper bound of the annual salary range in USD",
    "hourly_salary_min": "Lower bound of the hourly rate in USD",
    "hourly_salary_max": "Upper bound of the hourly rate in USD",
    "soc_code": "Standard Occupational Classification code",
    "soc_name": "Standard Occupational Classification title",
    "occupation_family": "Broad occupational family",
    "naics_code": "Industry code assigned by the data provider (aggregated form)",
    "naics_name": "Industry label",
    "onet_code": "O*NET occupation code",
    "onet_name": "O*NET occupation title",
    "cip_code": "Classification of Instructional Programs code",
    "cip_name": "Instructional program title",
    "program_matches": "MET degree programmes matched to the posting",
    "search_relevance_score": "API relevance score for the query used",
    "search_rank_reason": "API explanation of the relevance score",
    "apply_url": "Link to the employer application page",
    "skills_text": "Skill names flattened to a semicolon-separated string",
    "skills_count": "Number of skills attached to the posting",
    "experience_years_raw": "Years of experience parsed from the description (approximate)",
    "education_level_raw": "Highest degree keyword found in the description (approximate)",
}

DERIVED = {"normalized_title", "organization_name", "skills_text", "skills_count",
           "experience_years_raw", "education_level_raw"}

interim = pd.read_csv(INTERIM, compression="gzip", low_memory=False)
panel = pd.read_csv(PANEL, low_memory=False)

print("=== why rows were dropped as missing a required field ===")
for col in ["job_id", "title", "company_name", "posted_at"]:
    print(f"  {col:15} missing in interim: {int(interim[col].isna().sum())}")
print(f"  rows in interim: {len(interim)}  ->  rows in panel: {len(panel)}")

rows = []
for col in panel.columns:
    non_null = int(panel[col].notna().sum())
    sample = panel[col].dropna().astype(str)
    rows.append({
        "variable": col,
        "type": str(panel[col].dtype),
        "source": "derived in this project" if col in DERIVED else "MET Employability API",
        "non_null": non_null,
        "missing_pct": round(100 * (1 - non_null / len(panel)), 1),
        "example": (sample.iloc[0][:60] if len(sample) else ""),
        "description": DESCRIPTIONS.get(col, ""),
    })

dictionary = pd.DataFrame(rows)
dictionary.to_csv(OUT_CSV, index=False)

lines = ["# Data Dictionary - career_market_panel.csv", "",
         f"{len(panel)} rows, {len(panel.columns)} columns.", "",
         "| Variable | Type | Source | Non-null | Missing % | Description |",
         "|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| `{r['variable']}` | {r['type']} | {r['source']} | "
                 f"{r['non_null']} | {r['missing_pct']}% | {r['description']} |")
with open(OUT_MD, "w") as handle:
    handle.write("\n".join(lines) + "\n")

print(f"\nwritten: {OUT_CSV} and {OUT_MD}")
print(dictionary[["variable", "type", "non_null", "missing_pct"]].to_string(index=False))
