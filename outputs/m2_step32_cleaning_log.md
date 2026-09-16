# Step 3.2 - Cleaning Core Variables

Generated: 2026-09-16 00:25
Source: `data/interim/jobs_naics523_filtered_20260915.csv.gz`
Output: `data/processed/career_market_panel.csv`

## Cleaning actions

- input rows: 6199
- dropped 0 duplicate postings (same job_id)
- dropped 0 rows missing a required field (job_id, title, company_name, posted_at)
- cleared 1 expires_at values that preceded posted_at
- cleared 0 latitude/longitude pairs outside US bounds
- swapped 0 reversed annual salary min/max pairs
- cleared 44 implausible annual salaries (below 10,000 or above 1,000,000)
- final row count: 6199
- analytical panel written to data/processed/career_market_panel.csv: 6199 rows, 43 columns
- columns excluded from the panel (full posting text and nested blobs): description, bls, census, student_signals, staffing_evidence

## Field coverage after cleaning

| Field | Rows populated | Share |
|---|---|---|
| annual salary present | 1206 | 19% |
| hourly salary present | 258 | 4% |
| state_code present | 1761 | 28% |
| remote_status known | 2992 | 48% |
| experience_years_raw present | 4093 | 66% |
| education_level_raw present | 3675 | 59% |
