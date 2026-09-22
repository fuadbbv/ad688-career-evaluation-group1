import pandas as pd

df = pd.read_parquet("data/interim/wrds_naics523_role_probe.parquet")
print(f"rows: {len(df):,}")

print("\n=== SALARY ===")
print("dtype:", df["SALARY"].dtype)
print("populated:", int(df["SALARY"].notna().sum()))
print("sample values:")
print(df["SALARY"].dropna().head(10).to_list())

numeric = pd.to_numeric(df["SALARY"], errors="coerce")
print("convert to number succeeds on:", int(numeric.notna().sum()))
print("describe:")
print(numeric.describe())

for col in ["SALARY_FROM", "SALARY_TO"]:
    values = pd.to_numeric(df[col], errors="coerce")
    print(f"\n=== {col} ===")
    print(f"populated: {int(values.notna().sum()):,}")
    print(values.describe())
    print("below 10,000:", int((values < 10_000).sum()))
