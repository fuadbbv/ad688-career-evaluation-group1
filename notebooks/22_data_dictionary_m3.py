"""Data dictionary for the Module 3 analytical panel."""
import pandas as pd

PANEL = "data/processed/career_market_panel.csv"
OUT_CSV = "outputs/data_dictionary.csv"
OUT_MD = "outputs/data_dictionary.md"

DESCRIPTIONS = {
    "ID": "Unique posting identifier from the source dataset; used to deduplicate",
    "POSTED": "Date the posting was published",
    "EXPIRED": "Date the posting expired; cleared when earlier than POSTED",
    "DURATION": "Days the posting stayed active, where the source records it",
    "URL": "Link to the original posting",
    "TITLE_RAW": "Job title exactly as published by the employer",
    "TITLE_NAME": "Normalised job title from the provider",
    "TITLE_CLEAN": "Title lowercased and trimmed, for grouping",
    "COMPANY_NAME": "Employer name",
    "COMPANY_IS_STAFFING": "Flag for postings placed by a staffing agency",
    "IS_INTERNSHIP": "Flag for internship postings",
    "EDUCATION_LEVELS_NAME": "All education levels mentioned in the posting",
    "MIN_EDULEVELS_NAME": "Lowest education level the posting accepts",
    "MAX_EDULEVELS_NAME": "Highest education level the posting mentions",
    "EMPLOYMENT_TYPE_NAME": "Full-time, part-time, contract and similar",
    "MIN_YEARS_EXPERIENCE": "Minimum years of experience required",
    "MAX_YEARS_EXPERIENCE": "Upper end of the experience range, where given",
    "SALARY": "Free-text salary summary from the provider; mostly an empty placeholder, kept for reference only",
    "SALARY_FROM": "Lower bound of the posted pay range, in the units of SALARY_PERIOD",
    "SALARY_TO": "Upper bound of the posted pay range, in the units of SALARY_PERIOD",
    "SALARY_PERIOD": "Pay period the range was quoted in: annual, hourly or monthly",
    "ANNUAL_SALARY_FROM": "Lower bound, annual postings only",
    "ANNUAL_SALARY_TO": "Upper bound, annual postings only",
    "ANNUAL_SALARY_MID": "Midpoint of the annual range; the field to use for salary analysis",
    "REMOTE_TYPE_NAME": "Remote, hybrid or onsite, where the posting states it",
    "LOCATION": "Free-text location as published",
    "CITY_NAME": "City",
    "COUNTY_NAME": "County",
    "MSA_NAME": "Metropolitan statistical area",
    "STATE": "Two-letter state code",
    "STATE_NAME": "State name",
    "NAICS2_NAME": "Industry sector label (2-digit)",
    "NAICS3": "Industry subsector code (3-digit) — 523 for every row in this panel",
    "NAICS3_NAME": "Industry subsector label",
    "NAICS4": "Industry group code (4-digit)",
    "NAICS4_NAME": "Industry group label",
    "NAICS5_NAME": "Industry label (5-digit)",
    "NAICS6_NAME": "National industry label (6-digit)",
    "SOC_2021_4": "Standard Occupational Classification code, 2021 revision",
    "SOC_2021_4_NAME": "Occupation title",
    "SOC_2021_5_NAME": "Detailed occupation title",
    "ONET_NAME": "O*NET occupation title",
    "CIP4_NAME": "Instructional programme most associated with the role",
    "SKILLS_NAME": "All skills attached to the posting, semicolon-separated",
    "SPECIALIZED_SKILLS_NAME": "Domain and technical specialisations",
    "COMMON_SKILLS_NAME": "Transferable skills such as communication and teamwork",
    "SOFTWARE_SKILLS_NAME": "Named tools and software, such as Python, SQL or Tableau",
    "CERTIFICATIONS_NAME": "Certifications the posting requests",
    "SKILLS_COUNT": "Number of skills listed",
    "SOFTWARE_SKILLS_COUNT": "Number of named tools listed",
}

DERIVED = {"TITLE_CLEAN", "SALARY_PERIOD", "ANNUAL_SALARY_FROM",
           "ANNUAL_SALARY_TO", "ANNUAL_SALARY_MID", "SKILLS_COUNT",
           "SOFTWARE_SKILLS_COUNT"}

panel = pd.read_csv(PANEL, low_memory=False)
rows = []
for col in panel.columns:
    non_null = int(panel[col].notna().sum())
    sample = panel[col].dropna().astype(str)
    rows.append({
        "variable": col,
        "type": str(panel[col].dtype),
        "source": "derived in this project" if col in DERIVED else "WRDS jobs_2026 dataset",
        "non_null": non_null,
        "missing_pct": round(100 * (1 - non_null / len(panel)), 1),
        "example": sample.iloc[0][:60] if len(sample) else "",
        "description": DESCRIPTIONS.get(col, ""),
    })

pd.DataFrame(rows).to_csv(OUT_CSV, index=False)

lines = ["# Data Dictionary — career_market_panel.csv", "",
         f"{len(panel):,} rows, {len(panel.columns)} columns. "
         "Source: WRDS jobs_2026 dataset, scoped to NAICS 523 and the "
         "BI/Data Analyst career pathway.", "",
         "| Variable | Type | Source | Non-null | Missing % | Description |",
         "|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| `{r['variable']}` | {r['type']} | {r['source']} | "
                 f"{r['non_null']:,} | {r['missing_pct']}% | {r['description']} |")
with open(OUT_MD, "w") as handle:
    handle.write("\n".join(lines) + "\n")

print(f"written {OUT_CSV} and {OUT_MD}")
missing = [c for c in panel.columns if c not in DESCRIPTIONS]
print("columns without a description:", missing if missing else "none")
print(pd.DataFrame(rows)[["variable", "non_null", "missing_pct"]].to_string(index=False))
