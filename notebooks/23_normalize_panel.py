"""
Field normalization for the Module 3 panel.

Runs after 21_fix_salary.py and before any figure or analysis script.
Adds cleaned columns rather than overwriting the source fields, so the
raw provider values stay auditable.

Four problems found during Module 3 integration:

1. TITLE_NAME is overwritten with the occupation name on most of the
   SOC-labelled rows, so it cannot be used to describe job titles.
   TITLE_CLEAN is rebuilt from TITLE_RAW instead.
2. STATE_NAME mixes full state names, two-letter codes, the country
   "United States" and the non-place value "Remote".
3. REMOTE_TYPE_NAME carries a literal "Unknown" alongside true nulls,
   and spells the office category both "Onsite" and "On-site".
4. MIN_YEARS_EXPERIENCE uses 0 with MAX 1 as a placeholder band on
   senior postings, which drags the median to zero.

Input/output: data/processed/career_market_panel.csv (rewritten in place)
Log         : outputs/m3_normalization_log.md
"""
import re
import pandas as pd
from pathlib import Path

PANEL = Path("data/processed/career_market_panel.csv")
LOG = Path("outputs/m3_normalization_log.md")

STATE_CODES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "PR": "Puerto Rico", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}
NOT_A_STATE = {"", "united states", "usa", "us", "remote", "n/a", "na",
               "unknown", "none", "nan"}
REMOTE_MAP = {"remote": "Remote", "hybrid": "Hybrid",
              "hybrid remote": "Hybrid", "onsite": "Onsite",
              "on-site": "Onsite", "not remote": "Onsite"}
NOT_A_STATUS = {"", "unknown", "n/a", "na", "none", "nan"}

df = pd.read_csv(PANEL, low_memory=False)
log = ["# Module 3 panel normalization", "",
       f"Input: {len(df):,} rows, {df.shape[1]} columns", ""]


def note(text):
    print(text)
    log.append(text)


# 1. Job titles -------------------------------------------------------
is_soc = (df["SOC_2021_4_NAME"].notna()
          & (df["TITLE_NAME"].astype(str).str.strip().str.lower()
             == df["SOC_2021_4_NAME"].astype(str).str.strip().str.lower()))
df["TITLE_NAME_IS_SOC"] = is_soc
note(f"- TITLE_NAME equals the occupation name on {is_soc.sum():,} rows "
     f"({is_soc.mean():.0%} of the panel); flagged as TITLE_NAME_IS_SOC")


def clean_title(value):
    text = re.sub(r"\s+", " ", str(value)).strip().lower()
    text = re.sub(r"[\s,;:\-\u2013\u2014]+$", "", text)
    return text if text and text != "nan" else pd.NA


before = df["TITLE_CLEAN"].nunique()
df["TITLE_CLEAN"] = df["TITLE_RAW"].map(clean_title)
note(f"- TITLE_CLEAN rebuilt from TITLE_RAW: distinct titles "
     f"{before:,} -> {df['TITLE_CLEAN'].nunique():,}")

# 2. States -----------------------------------------------------------
def clean_state(value):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip()
    if text.lower() in NOT_A_STATE:
        return pd.NA
    if len(text) == 2 and text.upper() in STATE_CODES:
        return STATE_CODES[text.upper()]
    return text


df["STATE_CLEAN"] = df["STATE_NAME"].map(clean_state)
recoded = (df["STATE_NAME"].notna() & df["STATE_CLEAN"].isna()).sum()
note(f"- STATE_CLEAN: {df['STATE_CLEAN'].notna().sum():,} rows carry a real "
     f"state ({df['STATE_CLEAN'].notna().mean():.0%}); {recoded:,} values "
     f"discarded as country-level or non-geographic")
note(f"- distinct states before {df['STATE_NAME'].nunique():,}, "
     f"after {df['STATE_CLEAN'].nunique():,}")

# 3. Work arrangement -------------------------------------------------
def clean_remote(value):
    if pd.isna(value):
        return pd.NA
    text = str(value).strip().lower()
    if text in NOT_A_STATUS:
        return pd.NA
    return REMOTE_MAP.get(text, str(value).strip())


df["REMOTE_CLEAN"] = df["REMOTE_TYPE_NAME"].map(clean_remote)
note(f"- REMOTE_CLEAN: {df['REMOTE_CLEAN'].notna().sum():,} rows labelled "
     f"({df['REMOTE_CLEAN'].notna().mean():.0%}); categories "
     + ", ".join(f"{k} {v:,}" for k, v
                 in df['REMOTE_CLEAN'].value_counts().items()))

# 4. Experience -------------------------------------------------------
mn = pd.to_numeric(df["MIN_YEARS_EXPERIENCE"], errors="coerce")
mx = pd.to_numeric(df["MAX_YEARS_EXPERIENCE"], errors="coerce")
placeholder = (mn == 0) & (mx.isna() | (mx <= 1))
df["MIN_YEARS_EXP_CLEAN"] = mn.where(~placeholder)
usable = df["MIN_YEARS_EXP_CLEAN"].dropna()
note(f"- MIN_YEARS_EXP_CLEAN: dropped {placeholder.sum():,} rows carrying the "
     f"0-1 placeholder band; {len(usable):,} rows keep a stated requirement "
     f"({len(usable)/len(df):.0%})")
note(f"- stated requirement: median {usable.median():.0f} years, "
     f"quartiles {usable.quantile(.25):.0f} and {usable.quantile(.75):.0f}")

df.to_csv(PANEL, index=False)
note("")
note(f"Output: {len(df):,} rows, {df.shape[1]} columns")
LOG.write_text("\n".join(log) + "\n")
print(f"\nwritten {PANEL} and {LOG}")
