# Module 3 panel normalization

Input: 7,074 rows, 50 columns

- TITLE_NAME equals the occupation name on 2,165 rows (31% of the panel); flagged as TITLE_NAME_IS_SOC
- TITLE_CLEAN rebuilt from TITLE_RAW: distinct titles 2,396 -> 4,000
- STATE_CLEAN: 5,135 rows carry a real state (73%); 1,397 values discarded as country-level or non-geographic
- distinct states before 173, after 126
- REMOTE_CLEAN: 3,126 rows labelled (44%); categories Hybrid 1,490, Remote 1,005, Onsite 631
- MIN_YEARS_EXP_CLEAN: dropped 2,239 rows carrying the 0-1 placeholder band; 1,702 rows keep a stated requirement (24%)
- stated requirement: median 3 years, quartiles 2 and 5

Output: 7,074 rows, 54 columns
