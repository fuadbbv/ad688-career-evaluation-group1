# Module 5 — regression on compensation

- postings with an annual salary midpoint: 1,741 of 7,074 (25%)
- salary range $25,000 to $696,000, median $112,500
- features: 179 skill indicators; specification B adds 13 geography and work-arrangement controls

**A: skills only**
- held-out R-squared (log scale): 0.366
- 5-fold cross-validated R-squared: 0.299 (sd 0.034)
- RMSE $40,930 | MAE $28,751

**B: skills + controls**
- held-out R-squared (log scale): 0.373
- 5-fold cross-validated R-squared: 0.319 (sd 0.036)
- RMSE $40,821 | MAE $28,552

**Baseline: predict the median for every posting**
- R-squared: -0.014
- RMSE $51,224 | MAE $36,576

Coefficients below are limited to the 107 skills appearing in at least 30 of the 1,741 postings that disclose pay. 72 rarer skills are estimated but not reported, because the data cannot support them.

Skills associated with higher pay (percentage effect, specification B):
   +22.0%   advanced analytics                 (  33 postings)
   +20.1%   executive leadership               (  33 postings)
   +18.9%   data architecture                  (  53 postings)
   +18.1%   technical accounting               (  45 postings)
   +17.3%   public accounting                  (  53 postings)
   +17.2%   real estate                        (  36 postings)
   +16.9%   data science                       (  88 postings)
   +15.5%   product management                 (  30 postings)
   +15.3%   fixed income                       (  46 postings)
   +15.3%   capital markets                    (  44 postings)
   +15.0%   critical thinking                  (  40 postings)
   +13.2%   strategic planning                 (  36 postings)

Skills associated with lower pay:
   -27.6%   problem solving                    (  76 postings)
   -18.7%   financial data                     (  95 postings)
   -16.4%   customer service                   (  69 postings)
   -11.8%   risk management framework          (  43 postings)
   -11.8%   organizational skills              ( 115 postings)
   -11.7%   microsoft office                   ( 235 postings)
   -10.1%   accounts payable                   (  31 postings)
    -9.4%   financial analysis                 ( 145 postings)
    -9.0%   microsoft excel                    ( 779 postings)
    -8.8%   power bi                           ( 156 postings)
    -8.5%   time management                    (  42 postings)
    -7.6%   risk analysis                      (  44 postings)
