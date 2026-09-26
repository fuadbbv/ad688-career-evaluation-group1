# Data Dictionary - career_market_panel.csv

6199 rows, 43 columns.

| Variable | Type | Source | Non-null | Missing % | Description |
|---|---|---|---|---|---|
| `job_id` | int64 | MET Employability API | 6199 | 0.0% | Unique posting identifier assigned by the MET API; used to deduplicate |
| `posted_at` | str | MET Employability API | 6199 | 0.0% | Date the posting was published |
| `expires_at` | str | MET Employability API | 422 | 93.2% | Date the posting expires; cleared when earlier than posted_at |
| `title` | str | MET Employability API | 6199 | 0.0% | Job title as published by the employer |
| `normalized_title` | str | derived in this project | 6199 | 0.0% | Title lowercased and trimmed, for grouping |
| `company_name` | str | MET Employability API | 6199 | 0.0% | Employer name as published on the posting |
| `is_staffing_agency` | bool | MET Employability API | 6199 | 0.0% | True when the posting comes from a staffing agency |
| `staffing_confidence` | float64 | MET Employability API | 6199 | 0.0% | API confidence score that the poster is a staffing agency |
| `location_text` | str | MET Employability API | 6078 | 2.0% | Free-text location as published |
| `city` | str | MET Employability API | 4958 | 20.0% | City parsed from the location |
| `city_code` | float64 | MET Employability API | 0 | 100.0% | Internal city identifier |
| `state` | str | MET Employability API | 5266 | 15.1% | State name |
| `state_code` | str | MET Employability API | 1761 | 71.6% | Two-letter US state code; empty for non-US postings |
| `zip_code` | float64 | MET Employability API | 39 | 99.4% | Five-digit ZIP code; 00000 treated as missing |
| `msa_code` | float64 | MET Employability API | 281 | 95.5% | Metropolitan statistical area code |
| `msa_name` | str | MET Employability API | 281 | 95.5% | Metropolitan statistical area name |
| `latitude` | float64 | MET Employability API | 59 | 99.0% | Latitude; cleared when outside US bounds |
| `longitude` | float64 | MET Employability API | 59 | 99.0% | Longitude; cleared when outside US bounds |
| `remote_status` | str | MET Employability API | 6199 | 0.0% | remote, hybrid, onsite or unknown |
| `employment_type` | str | MET Employability API | 5017 | 19.1% | Full-time, part-time, contract and similar |
| `salary_text` | str | MET Employability API | 4106 | 33.8% | Raw salary block as returned by the API |
| `annual_salary_min` | float64 | MET Employability API | 1206 | 80.5% | Lower bound of the annual salary range in USD |
| `annual_salary_max` | float64 | MET Employability API | 1206 | 80.5% | Upper bound of the annual salary range in USD |
| `hourly_salary_min` | float64 | MET Employability API | 258 | 95.8% | Lower bound of the hourly rate in USD |
| `hourly_salary_max` | float64 | MET Employability API | 258 | 95.8% | Upper bound of the hourly rate in USD |
| `soc_code` | str | MET Employability API | 6092 | 1.7% | Standard Occupational Classification code |
| `soc_name` | str | MET Employability API | 6092 | 1.7% | Standard Occupational Classification title |
| `occupation_family` | str | MET Employability API | 6092 | 1.7% | Broad occupational family |
| `naics_code` | int64 | MET Employability API | 6199 | 0.0% | Industry code assigned by the data provider (aggregated form) |
| `naics_name` | str | MET Employability API | 6199 | 0.0% | Industry label |
| `onet_code` | str | MET Employability API | 6096 | 1.7% | O*NET occupation code |
| `onet_name` | str | MET Employability API | 6096 | 1.7% | O*NET occupation title |
| `cip_code` | float64 | MET Employability API | 261 | 95.8% | Classification of Instructional Programs code |
| `cip_name` | str | MET Employability API | 261 | 95.8% | Instructional program title |
| `program_matches` | str | MET Employability API | 6199 | 0.0% | MET degree programmes matched to the posting |
| `search_relevance_score` | int64 | MET Employability API | 6199 | 0.0% | API relevance score for the query used |
| `search_rank_reason` | str | MET Employability API | 6199 | 0.0% | API explanation of the relevance score |
| `apply_url` | str | MET Employability API | 5128 | 17.3% | Link to the employer application page |
| `skills_text` | str | derived in this project | 5742 | 7.4% | Skill names flattened to a semicolon-separated string |
| `skills_count` | int64 | derived in this project | 6199 | 0.0% | Number of skills attached to the posting |
| `experience_years_raw` | float64 | derived in this project | 4093 | 34.0% | Years of experience parsed from the description (approximate) |
| `education_level_raw` | str | derived in this project | 3675 | 40.7% | Highest degree keyword found in the description (approximate) |
| `organization_name` | str | derived in this project | 3371 | 45.6% | Employer name from the linked organization record |
