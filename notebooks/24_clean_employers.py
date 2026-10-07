"""
Employer field cleanup for the Module 5 analytics.

Does not drop rows. Adds three columns so the panel row count stays 7,074
and every published figure outside the employer section stays valid:

  EMPLOYER_CLEAN          canonical employer name
  EMPLOYER_UNIDENTIFIED   True where the field holds an applicant-tracking
                          hostname rather than a company name
  IS_AGENCY               True for staffing agencies and job aggregators

Why flag rather than filter: the provider's COMPANY_IS_STAFFING is set on
only 93 of 7,074 rows and contradicts itself (TD is flagged as staffing,
JPMorgan Chase carries both values), so it cannot be used on its own.

Input/output: data/processed/career_market_panel.csv (rewritten in place)
Log         : outputs/m5_employer_cleanup_log.md
"""
import re
import pandas as pd
from pathlib import Path

PANEL = Path("data/processed/career_market_panel.csv")
LOG = Path("outputs/m5_employer_cleanup_log.md")

# Hostnames and spelling variants that refer to one employer
CANONICAL = {
    "careers.usbank.com": "U.S. Bank",
    "usbank": "U.S. Bank",
    "careers.statestreet.com": "State Street",
    "jobs.thermofisher.com": "Thermo Fisher Scientific",
    "jpmorganchase": "JPMorgan Chase",
    "jpmorgan chase & co.": "JPMorgan Chase",
    "jpmorgan chase": "JPMorgan Chase",
    "oldnational": "Old National Bank",
    "icapitalnetwork": "iCapital",
    "prosidianconsulting": "ProSidian Consulting",
}

# Applicant-tracking hostnames that identify no company at all
HOSTNAME = re.compile(r"(?:oraclecloud\.com|myworkdayjobs|taleo|icims|"
                      r"greenhouse\.io|lever\.co|smartrecruiters)", re.I)

# Staffing agencies and job aggregators, matched conservatively
AGENCY_EXACT = {
    "jobgether", "jobs via dice", "global technical talent, an inc. 5000 company",
    "robert half", "apex systems", "kforce inc", "kforce", "cybercoders",
    "motion recruitment", "talentally", "suppliedtalent", "jobot",
    "insight global", "teksystems", "randstad", "adecco", "aerotek",
    "experis", "collabera", "diverse lynx", "mindlance", "hays",
    "michael page", "mthreerecruitingportal",
}
AGENCY_PATTERN = re.compile(
    r"\bstaffing\b|\brecruiting\b|\brecruitment\b|\brecruiters?\b|"
    r"search\s*\|?\s*staffing|job\s*board", re.I)

df = pd.read_csv(PANEL, low_memory=False)
log = ["# Module 5 employer cleanup", "", f"Panel: {len(df):,} rows", ""]


def note(text):
    print(text)
    log.append(text)


raw = df["COMPANY_NAME"].fillna("").astype(str).str.strip()
key = raw.str.lower()

df["EMPLOYER_CLEAN"] = key.map(CANONICAL).fillna(raw).replace("", pd.NA)
renamed = (key.isin(CANONICAL)).sum()
note(f"- canonical names applied to {renamed:,} rows "
     f"({len(CANONICAL)} mappings)")

df["EMPLOYER_UNIDENTIFIED"] = raw.str.contains(HOSTNAME, na=False)
note(f"- applicant-tracking hostnames in the employer field: "
     f"{df['EMPLOYER_UNIDENTIFIED'].sum():,} rows "
     f"({df['EMPLOYER_UNIDENTIFIED'].mean():.1%})")

df["IS_AGENCY"] = key.isin(AGENCY_EXACT) | raw.str.contains(AGENCY_PATTERN, na=False)
note(f"- staffing agencies and aggregators flagged: {df['IS_AGENCY'].sum():,} rows "
     f"({df['IS_AGENCY'].mean():.1%})")

note("")
note("Employers flagged as agencies:")
for name, n in df.loc[df["IS_AGENCY"], "EMPLOYER_CLEAN"].value_counts().items():
    note(f"  {n:>4,}  {name}")

note("")
note("Top employers after cleaning, agencies and unidentified excluded:")
real = df[~df["IS_AGENCY"] & ~df["EMPLOYER_UNIDENTIFIED"]]
top = real["EMPLOYER_CLEAN"].dropna().value_counts()
for name, n in top.head(12).items():
    note(f"  {n:>4,}  {name}  ({n/len(real):.1%})")
note("")
note(f"- distinct employers, before {df['COMPANY_NAME'].nunique():,}, "
     f"after {real['EMPLOYER_CLEAN'].nunique():,}")
note(f"- analysable employer rows: {len(real):,} of {len(df):,} "
     f"({len(real)/len(df):.0%})")
note(f"- top 10 employers hold {top.head(10).sum()/len(real):.0%} of those rows")

df.to_csv(PANEL, index=False)
LOG.write_text("\n".join(log) + "\n")
print(f"\nwritten {PANEL} ({len(df):,} x {df.shape[1]}) and {LOG}")
