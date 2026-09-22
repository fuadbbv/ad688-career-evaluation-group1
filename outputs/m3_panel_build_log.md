# Module 3 - Analytical Panel Build

Generated: 2026-09-22 23:43
Source: WRDS jobs_2026 dataset (504,208 postings, 134 columns)
Scope: NAICS 523, postings from 2025-09-01 onward
Output: `data/processed/career_market_panel.csv`

## Build steps

- postings in NAICS 523: 24,914
- matched the role definition: 8,747
- removed as information-security roles: 76
- removed for no publication date: 1,405
- removed as published before 2025-09-01: 192
- dropped 0 duplicate postings (same ID)
- dropped 0 rows missing a required field (ID, TITLE_NAME, COMPANY_NAME, POSTED)
- cleared 0 expiry dates that preceded the posting date
- swapped 0 reversed salary min/max pairs
- cleared 367 implausible salary ranges and 0 implausible single salary values (below 10,000 or above 1,000,000)
- final row count: 7,074
- panel written to data/processed/career_market_panel.csv: 7,074 rows, 47 columns

## Field coverage

| Field | Populated | Share |
|---|---|---|
| salary (any figure) | 1,742 | 25% |
| salary range (from/to) | 1,742 | 25% |
| US state | 6,532 | 92% |
| remote type | 4,568 | 65% |
| minimum years of experience | 3,941 | 56% |
| minimum education level | 4,913 | 69% |
| skills | 7,074 | 100% |
| software skills | 7,074 | 100% |
| occupation (SOC 2021) | 2,357 | 33% |
