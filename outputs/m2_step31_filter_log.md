# Step 3.1 - Filtered Industry-Career Dataset

Generated: 2026-09-15 01:29

## Scope
- Industry: NAICS 523 (Securities, Commodity Contracts and Other Financial Investments)
- Career pathway: Business Intelligence / Data Analyst
- Date window: postings with posted_at >= 2025-09-01
- Source: MET Employability Career Match API, endpoint `/student/jobs/`

## Filter funnel
- Postings pulled for the industry and date window: 15176
- Matched the role definition (SOC or title): 6263
- Removed as out-of-scope (information security roles): 64
- Removed as duplicate job_id: 0
- **Final analytical dataset: 6199 rows**

## Role definition
- SOC contains: `data scientist|database architect|statistician|mathematician|operations research|market research analyst|financial and investment analyst|credit analyst|management analyst`
- OR title contains: `\banalyst\b|\banalytics\b|\bdata\b|business intelligence|\bbi\b|reporting|\bsql\b|data scien|machine learning`
- Excluded SOC: `information security`; excluded title: `security analyst|soc analyst`

## Derived columns added in this step
- `skills_text` - skill names flattened to a semicolon-separated string
- `skills_count` - number of skills listed
- `experience_years_raw` - first 'N years' figure found in the description (UNCLEANED)
- `education_level_raw` - highest degree keyword found in the description (UNCLEANED)
- `organization_name` - employer name lifted out of the nested organization object

## Known data-quality issues to handle in Step 3.2
- Missing state_code: 4438 of 6199
- remote_status = unknown: 3207 of 6199
- Missing annual_salary_min: 4949 of 6199
- Missing hourly_salary_min: 5941 of 6199
- experience_years_raw not found: 2106 of 6199
- education_level_raw not found: 2524 of 6199

## Output
- `data/interim/jobs_naics523_filtered_20260915.csv.gz` (6199 rows, 48 columns)
- Raw API response kept locally at `data/raw/jobs_naics523_raw_20260915.json` (git-ignored)
