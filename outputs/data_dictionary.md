# Data Dictionary — career_market_panel.csv

7,074 rows, 50 columns. Source: WRDS jobs_2026 dataset, scoped to NAICS 523 and the BI/Data Analyst career pathway.

| Variable | Type | Source | Non-null | Missing % | Description |
|---|---|---|---|---|---|
| `ID` | int64 | WRDS jobs_2026 dataset | 7,074 | 0.0% | Unique posting identifier from the source dataset; used to deduplicate |
| `POSTED` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Date the posting was published |
| `EXPIRED` | str | WRDS jobs_2026 dataset | 365 | 94.8% | Date the posting expired; cleared when earlier than POSTED |
| `DURATION` | float64 | WRDS jobs_2026 dataset | 365 | 94.8% | Days the posting stayed active, where the source records it |
| `URL` | str | WRDS jobs_2026 dataset | 5,808 | 17.9% | Link to the original posting |
| `TITLE_RAW` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Job title exactly as published by the employer |
| `TITLE_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Normalised job title from the provider |
| `TITLE_CLEAN` | str | derived in this project | 7,074 | 0.0% | Title lowercased and trimmed, for grouping |
| `COMPANY_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Employer name |
| `COMPANY_IS_STAFFING` | float64 | WRDS jobs_2026 dataset | 2,357 | 66.7% | Flag for postings placed by a staffing agency |
| `IS_INTERNSHIP` | int64 | WRDS jobs_2026 dataset | 7,074 | 0.0% | Flag for internship postings |
| `EDUCATION_LEVELS_NAME` | str | WRDS jobs_2026 dataset | 6,445 | 8.9% | All education levels mentioned in the posting |
| `MIN_EDULEVELS_NAME` | str | WRDS jobs_2026 dataset | 4,913 | 30.5% | Lowest education level the posting accepts |
| `MAX_EDULEVELS_NAME` | str | WRDS jobs_2026 dataset | 6,445 | 8.9% | Highest education level the posting mentions |
| `EMPLOYMENT_TYPE_NAME` | str | WRDS jobs_2026 dataset | 5,537 | 21.7% | Full-time, part-time, contract and similar |
| `MIN_YEARS_EXPERIENCE` | float64 | WRDS jobs_2026 dataset | 3,941 | 44.3% | Minimum years of experience required |
| `MAX_YEARS_EXPERIENCE` | float64 | WRDS jobs_2026 dataset | 2,625 | 62.9% | Upper end of the experience range, where given |
| `SALARY` | float64 | WRDS jobs_2026 dataset | 0 | 100.0% | Free-text salary summary from the provider; mostly an empty placeholder, kept for reference only |
| `REMOTE_TYPE_NAME` | str | WRDS jobs_2026 dataset | 4,568 | 35.4% | Remote, hybrid or onsite, where the posting states it |
| `LOCATION` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Free-text location as published |
| `CITY_NAME` | str | WRDS jobs_2026 dataset | 6,140 | 13.2% | City |
| `COUNTY_NAME` | str | WRDS jobs_2026 dataset | 435 | 93.9% | County |
| `MSA_NAME` | str | WRDS jobs_2026 dataset | 620 | 91.2% | Metropolitan statistical area |
| `STATE` | str | WRDS jobs_2026 dataset | 4,667 | 34.0% | Two-letter state code |
| `STATE_NAME` | str | WRDS jobs_2026 dataset | 6,532 | 7.7% | State name |
| `NAICS2_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Industry sector label (2-digit) |
| `NAICS3` | int64 | WRDS jobs_2026 dataset | 7,074 | 0.0% | Industry subsector code (3-digit) — 523 for every row in this panel |
| `NAICS3_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Industry subsector label |
| `NAICS4` | float64 | WRDS jobs_2026 dataset | 27 | 99.6% | Industry group code (4-digit) |
| `NAICS4_NAME` | str | WRDS jobs_2026 dataset | 27 | 99.6% | Industry group label |
| `NAICS5_NAME` | str | WRDS jobs_2026 dataset | 25 | 99.6% | Industry label (5-digit) |
| `NAICS6_NAME` | str | WRDS jobs_2026 dataset | 24 | 99.7% | National industry label (6-digit) |
| `SOC_2021_4` | str | WRDS jobs_2026 dataset | 2,357 | 66.7% | Standard Occupational Classification code, 2021 revision |
| `SOC_2021_4_NAME` | str | WRDS jobs_2026 dataset | 2,357 | 66.7% | Occupation title |
| `SOC_2021_5_NAME` | str | WRDS jobs_2026 dataset | 2,357 | 66.7% | Detailed occupation title |
| `ONET_NAME` | str | WRDS jobs_2026 dataset | 6,905 | 2.4% | O*NET occupation title |
| `CIP4_NAME` | str | WRDS jobs_2026 dataset | 2,357 | 66.7% | Instructional programme most associated with the role |
| `SKILLS_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | All skills attached to the posting, semicolon-separated |
| `SPECIALIZED_SKILLS_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Domain and technical specialisations |
| `COMMON_SKILLS_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Transferable skills such as communication and teamwork |
| `SOFTWARE_SKILLS_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Named tools and software, such as Python, SQL or Tableau |
| `CERTIFICATIONS_NAME` | str | WRDS jobs_2026 dataset | 7,074 | 0.0% | Certifications the posting requests |
| `SKILLS_COUNT` | int64 | derived in this project | 7,074 | 0.0% | Number of skills listed |
| `SOFTWARE_SKILLS_COUNT` | int64 | derived in this project | 7,074 | 0.0% | Number of named tools listed |
| `SALARY_FROM` | float64 | WRDS jobs_2026 dataset | 2,064 | 70.8% | Lower bound of the posted pay range, in the units of SALARY_PERIOD |
| `SALARY_TO` | float64 | WRDS jobs_2026 dataset | 2,064 | 70.8% | Upper bound of the posted pay range, in the units of SALARY_PERIOD |
| `SALARY_PERIOD` | str | derived in this project | 2,064 | 70.8% | Pay period the range was quoted in: annual, hourly or monthly |
| `ANNUAL_SALARY_FROM` | float64 | derived in this project | 1,741 | 75.4% | Lower bound, annual postings only |
| `ANNUAL_SALARY_TO` | float64 | derived in this project | 1,741 | 75.4% | Upper bound, annual postings only |
| `ANNUAL_SALARY_MID` | float64 | derived in this project | 1,741 | 75.4% | Midpoint of the annual range; the field to use for salary analysis |
