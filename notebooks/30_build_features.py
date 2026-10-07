"""
Feature matrix for the Module 5 models.

One matrix, two models: the regression on compensation and the
classification of seniority both use the same binary skill indicators, so
the parsing and vocabulary decisions are made once and documented here.

Note on parsing: SKILLS_NAME holds a JSON list string, for example
["Microsoft Excel", "SQL (Programming Language)"]. Splitting it on a
delimiter silently turns a whole posting into one skill, so it is parsed
as JSON. Qualifiers in brackets are stripped, because "SQL (Programming
Language)" and "SQL" are the same skill to a job seeker.

Input : data/processed/career_market_panel.csv
Output: data/processed/model_features.parquet
        outputs/m5_feature_build_log.md
"""
import ast
import json
import re
import pandas as pd
from pathlib import Path

PANEL = Path("data/processed/career_market_panel.csv")
OUT = Path("data/processed/model_features.parquet")
LOG = Path("outputs/m5_feature_build_log.md")

MIN_SHARE = 0.01          # keep a skill if it appears in at least 1% of postings
ENTRY_MAX_YEARS = 2       # entry level: a stated requirement of 2 years or less

df = pd.read_csv(PANEL, low_memory=False)
log = ["# Module 5 feature matrix", "", f"Panel: {len(df):,} postings", ""]


def note(text):
    print(text)
    log.append(text)


def parse_skills(value):
    """SKILLS_NAME is a JSON list string, not a delimited string."""
    if pd.isna(value):
        return []
    text = str(value).strip()
    for loader in (json.loads, ast.literal_eval):
        try:
            parsed = loader(text)
            if isinstance(parsed, (list, tuple)):
                return [str(x) for x in parsed]
        except (ValueError, SyntaxError):
            continue
    return [text] if text else []


def normalise(skill):
    """Drop bracketed qualifiers: SQL (Programming Language) -> sql."""
    return re.sub(r"\s*\([^)]*\)", "", str(skill)).strip().lower()


skills = df["SKILLS_NAME"].map(parse_skills).map(
    lambda items: {normalise(s) for s in items if str(s).strip()})

empty = (skills.str.len() == 0).sum()
note(f"- parsed skill lists on {len(df) - empty:,} postings "
     f"({(len(df) - empty) / len(df):.0%}); {empty:,} empty")
note(f"- distinct skill names after normalisation: "
     f"{len({s for row in skills for s in row}):,}")
note(f"- median skills per posting: {skills.str.len().median():.0f}")

counts = pd.Series([s for row in skills for s in row]).value_counts()
vocab = counts[counts >= MIN_SHARE * len(df)].index.tolist()
note(f"- vocabulary kept: {len(vocab):,} skills appearing in at least "
     f"{MIN_SHARE:.0%} of postings ({int(MIN_SHARE * len(df)):,} postings)")

features = pd.DataFrame(
    {f"skill__{s}": skills.map(lambda row, s=s: int(s in row)) for s in vocab},
    index=df.index)

features.insert(0, "ID", df["ID"])
features["SALARY"] = pd.to_numeric(df["ANNUAL_SALARY_MID"], errors="coerce")
features["YEARS"] = pd.to_numeric(df["MIN_YEARS_EXP_CLEAN"], errors="coerce")
features["SENIORITY"] = features["YEARS"].apply(
    lambda y: pd.NA if pd.isna(y) else int(y > ENTRY_MAX_YEARS))
features["STATE"] = df["STATE_CLEAN"]
features["REMOTE"] = df["REMOTE_CLEAN"]
features["IS_AGENCY"] = df["IS_AGENCY"].fillna(False)

note("")
note("Model targets:")
note(f"- regression, postings with an annual salary: "
     f"{features['SALARY'].notna().sum():,}")
note(f"- classification, postings with a stated experience requirement: "
     f"{features['SENIORITY'].notna().sum():,}")
bal = features["SENIORITY"].value_counts(dropna=True)
note(f"  entry (<= {ENTRY_MAX_YEARS} years): {bal.get(0, 0):,} | "
     f"advanced (> {ENTRY_MAX_YEARS} years): {bal.get(1, 0):,}")

# --- Is there any signal? Compare the top and bottom salary quartiles -----
sal = features["SALARY"].dropna()
low_cut, high_cut = sal.quantile(0.25), sal.quantile(0.75)
low = features[features["SALARY"] <= low_cut]
high = features[features["SALARY"] >= high_cut]
note("")
note(f"Signal check: bottom quartile (<= ${low_cut:,.0f}, {len(low):,} postings) "
     f"vs top quartile (>= ${high_cut:,.0f}, {len(high):,} postings)")

cols = [c for c in features.columns if c.startswith("skill__")]
diff = pd.DataFrame({
    "top_%": high[cols].mean() * 100,
    "bottom_%": low[cols].mean() * 100,
})
diff["gap"] = diff["top_%"] - diff["bottom_%"]
diff.index = [c.replace("skill__", "") for c in diff.index]

note("")
note("Most over-represented in well-paid postings:")
for name, r in diff.sort_values("gap", ascending=False).head(15).iterrows():
    note(f"  {r['gap']:+6.1f} pp   {name[:42]:<44} "
         f"top {r['top_%']:5.1f}%  bottom {r['bottom_%']:5.1f}%")

note("")
note("Most over-represented in low-paid postings:")
for name, r in diff.sort_values("gap").head(10).iterrows():
    note(f"  {r['gap']:+6.1f} pp   {name[:42]:<44} "
         f"top {r['top_%']:5.1f}%  bottom {r['bottom_%']:5.1f}%")

features.to_parquet(OUT, index=False)
LOG.write_text("\n".join(log) + "\n")
print(f"\nwritten {OUT} ({features.shape[0]:,} x {features.shape[1]}) and {LOG}")
