import pandas as pd
import numpy as np
#column data types
##df= pd.read_csv('data/interim/jobs_naics523_filtered_20260915.csv.gz', compression='gzip')
##print(df.dtypes)

#assigning columns the correct types
date = ["posted_at", "expires_at"]
float = ["staffing_confidence","latitude","longitude","annual_salary_min","annual_salary_max","hourly_salary_min","hourly_salary_max",
         "experience_years_raw"]
category = ["state","state_code","remote_status","employment_type","soc_code","occupation_family","education_level_raw","cip_code",
            "job_id", "naics_code", "zip_code", "msa_code","city_code"]
##nullable_int = []
int= ["search_relevance_score", "skills_count"]
bool = ["is_staffing_agency"]
def cleaning(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
 #assigning correct data types to columns
    #Dates
    for col in date:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
 
    #Booleans
    for col in bool:
        if col in df.columns and df[col].dtype != bool:
            df[col] = df[col].astype("boolean")
 
    #int
    for col in int:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
 
    #Nullable int
    #for col in nullable_int:
    #    if col in df.columns:
     #       df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
 
    #Floats
    for col in float:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    
    #Categoricals    
    numeric_category = {"zip_code", "naics_code", "msa_code", "cip_code"}
    for col in category:
        if col not in df.columns:
            continue
        #taking into account the fact that these columns are imported as numbers with .0 at the end
        if col in numeric_category:
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric = pd.to_numeric(df[col], errors="coerce")
 
                def _to_int_str(x):
                    try:
                        if pd.isna(x) or not np.isfinite(x):
                            return pd.NA
                        return str(int(x))
                    except (ValueError, OverflowError, TypeError):
                        return pd.NA
 
                df[col] = numeric.map(_to_int_str).astype("string")
            else:
                s = df[col].astype("string")
                s = s.str.replace(r"^(-?\d+)\.0$", r"\1", regex=True)
                s = s.replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
                df[col] = s
 
        df[col] = df[col].astype("category")
         
    #others
    already_typed = set(
        date + bool + int + float + category #+ nullable_int 
    )
    remaining_cols = [c for c in df.columns if c not in already_typed]
    for col in remaining_cols:
        df[col] = df[col].astype("string")
 
#cleaning data   
    #duplicate postings
    df = df.drop_duplicates(subset="job_id")
    df = df.reset_index(drop=True)
    print(f"dropped {rows_before - len(df)} duplicate rows")
 
    #rows missing anything important
    required = ["job_id", "title", "company_name", "posted_at"]
    rows_before = len(df)
    df = df.dropna(subset=required)
    print(f"dropped {rows_before - len(df)} rows missing required fields")
 
    #checking date logic
    bad_dates = df["expires_at"] < df["posted_at"]
    df.loc[bad_dates, "expires_at"] = pd.NaT
    print(f"cleared {bad_dates.sum()} bad expires_at values")
 
    #cleaning whitespace
    text_columns = ["title", "company_name", "city", "state"]
    for col in text_columns:
        df[col] = df[col].str.strip()
 
    df["normalized_title"] = df["title"].str.lower().str.strip()
 
    #zip codes to 5 digits
    df["zip_code"] = df["zip_code"].str.strip().str.zfill(5)
    df.loc[df["zip_code"] == "00000", "zip_code"] = pd.NA
 
    #check within the us
    in_us = df["latitude"].between(18, 72) & df["longitude"].between(-180, -65)
    df.loc[~in_us, ["latitude", "longitude"]] = pd.NA
    print(f"cleared {(~in_us).sum()} out-of-range lat/long values")
 
    #fixing invalid salary range
    swapped = df["annual_salary_min"] > df["annual_salary_max"]
    df.loc[swapped, ["annual_salary_min", "annual_salary_max"]] = (
        df.loc[swapped, ["annual_salary_max", "annual_salary_min"]].values
    )
    print(f"swapped {swapped.sum()} min/max salary pairs")
 
    too_low = df["annual_salary_min"] < 10000
    too_high = df["annual_salary_max"] > 1000000
    bad_salary = too_low | too_high
    df.loc[bad_salary, ["annual_salary_min", "annual_salary_max"]] = pd.NA
    print(f"cleared {bad_salary.sum()} out-of-range salary values")
 
    #strip long text fields
    df["description"] = df["description"].str.replace(r"<[^>]+>", " ", regex=True)
    df["description"] = df["description"].str.replace(r"\s+", " ", regex=True).str.strip()
 
    #standardizing values (commening out but leaving incase we want to satndardize)
   # remote_map = {
    #    "x": "remote",
     #   "x": "remote",
    #    "y": "hybrid",
     #   "z": "onsite",
    #   "z": "onsite",
     #   "z": "onsite",
    #}
    #df["remote_status"] = df["remote_status"].astype("string").str.lower().str.strip()
    #df["remote_status"] = df["remote_status"].map(remote_map).astype("category")
 
    return df
 
 
def main():
    df = pd.read_csv('data/interim/jobs_naics523_cleaned_20260915.csv.gz', compression="gzip", low_memory=False)
    df = clean_data(df)
 
    print(df.dtypes)
    print(f"final row count: {len(df)}")
 
   
    return df
 
 
def main():
    df = pd.read_csv('data/interim/jobs_naics523_filtered_20260915.csv.gz', compression="gzip", low_memory=False)
    df = cleaning(df)
 
    print(df.dtypes)
 
    df.to_csv('data/interim/jobs_naics523_cleaned_20260915.csv.gz', index=False, compression="gzip")
    print(f"\nSaved typed CSV to { 'data/interim/jobs_naics523_cleaned_20260915.csv.gz'}")
 
   

 

 