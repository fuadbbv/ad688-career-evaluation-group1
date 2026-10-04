# Module 5 feature matrix

Panel: 7,074 postings

- parsed skill lists on 6,878 postings (97%); 196 empty
- distinct skill names after normalisation: 3,327
- median skills per posting: 10
- vocabulary kept: 179 skills appearing in at least 1% of postings (70 postings)

Model targets:
- regression, postings with an annual salary: 1,741
- classification, postings with a stated experience requirement: 1,702
  entry (<= 2 years): 542 | advanced (> 2 years): 1,160

Signal check: bottom quartile (<= $87,500, 448 postings) vs top quartile (>= $141,500, 437 postings)

Most over-represented in well-paid postings:
   +23.1 pp   python                                       top  33.0%  bottom   9.8%
   +15.8 pp   sql                                          top  35.0%  bottom  19.2%
   +12.6 pp   data science                                 top  12.6%  bottom   0.0%
    +7.6 pp   machine learning                             top   7.6%  bottom   0.0%
    +6.2 pp   databricks                                   top   6.2%  bottom   0.0%
    +5.5 pp   fixed income                                 top   6.2%  bottom   0.7%
    +5.3 pp   public accounting                            top   5.9%  bottom   0.7%
    +5.3 pp   data engineering                             top   5.3%  bottom   0.0%
    +5.0 pp   a/b testing                                  top   5.0%  bottom   0.0%
    +4.9 pp   computer science                             top   6.9%  bottom   2.0%
    +4.8 pp   stakeholder management                       top   4.8%  bottom   0.0%
    +4.6 pp   technical accounting                         top   5.5%  bottom   0.9%
    +4.4 pp   advanced analytics                           top   4.8%  bottom   0.4%
    +4.3 pp   data pipelines                               top   4.3%  bottom   0.0%
    +4.1 pp   business intelligence                        top   4.6%  bottom   0.4%

Most over-represented in low-paid postings:
   -26.2 pp   microsoft excel                              top  25.6%  bottom  51.8%
   -22.4 pp   microsoft office                             top   5.0%  bottom  27.5%
   -12.2 pp   organizational skills                        top   2.1%  bottom  14.3%
    -8.2 pp   customer service                             top   1.6%  bottom   9.8%
    -7.7 pp   financial analysis                           top   3.0%  bottom  10.7%
    -7.5 pp   risk management                              top   5.5%  bottom  12.9%
    -7.4 pp   verbal communication skills                  top   8.7%  bottom  16.1%
    -6.4 pp   accounting                                   top   3.2%  bottom   9.6%
    -5.8 pp   analytical skills                            top   7.6%  bottom  13.4%
    -5.5 pp   power bi                                     top   5.3%  bottom  10.7%
