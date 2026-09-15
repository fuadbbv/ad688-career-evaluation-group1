import pandas as pd
df = pd.read_csv('data/interim/jobs_naics523_filtered_20260915.csv.gz', compression="gzip", low_memory=False, nrows=5)
print(df)