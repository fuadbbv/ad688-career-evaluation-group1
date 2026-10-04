# Module 5 — classification of seniority

- postings with a stated experience requirement: 1,702 of 7,074 (24%)
- entry level (2 years or less): 542 (32%)
- advanced (more than 2 years): 1,160 (68%)
- features: 179 binary skill indicators

**Held-out performance (25 percent of postings, never seen in training)**
- accuracy: 0.678
- ROC AUC: 0.741
- entry     precision 0.497 | recall 0.669 | F1 0.571 | n = 136
- advanced  precision 0.815 | recall 0.683 | F1 0.743 | n = 290

**Baseline: label every posting as the majority class**
- accuracy: 0.681
- recall on the entry class: 0.000 — the baseline never identifies the postings a student can actually apply to, which is the whole point

Confusion matrix (rows = actual, columns = predicted):
            predicted entry   predicted advanced
  entry                91                   45
  advanced             92                  198

```
              precision    recall  f1-score   support

       entry       0.50      0.67      0.57       136
    advanced       0.81      0.68      0.74       290

    accuracy                           0.68       426
   macro avg       0.66      0.68      0.66       426
weighted avg       0.71      0.68      0.69       426

```

Odds ratios for the 109 skills appearing in at least 30 of these postings. Above 1 means the skill makes a posting more likely to be advanced; below 1, more likely entry level.

Completely separated (2 skills): every posting listing these falls on one side of the split, so the odds ratio is an artifact of that and only the direction can be read.
  treasury management                (  57 postings, 98% advanced)
  data architecture                  (  52 postings, 100% advanced)

Base rate: 68% of these postings are advanced. A skill is reported below only when its coefficient and its raw share point the same way; 21 of 107 do not and are listed afterwards.

Strongest markers of an advanced posting:
  x 96.86   data governance                    (  35 postings, 97% advanced)
  x 16.77   technical accounting               (  41 postings, 88% advanced)
  x 14.78   information technology             (  58 postings, 97% advanced)
  x 12.49   bank secrecy act                   (  44 postings, 98% advanced)
  x 10.18   general ledger                     (  34 postings, 85% advanced)
  x  9.32   operational excellence             (  36 postings, 89% advanced)
  x  8.75   risk analytics                     (  30 postings, 83% advanced)
  x  8.06   risk appetite                      (  44 postings, 89% advanced)
  x  6.38   business requirements              (  81 postings, 91% advanced)
  x  5.89   business systems                   (  31 postings, 87% advanced)
  x  4.70   business intelligence              (  40 postings, 98% advanced)
  x  4.19   public accounting                  (  32 postings, 84% advanced)

Strongest markers of an entry-level posting:
  x  0.15   research                           (  36 postings, 28% advanced)
  x  0.22   business development               (  58 postings, 47% advanced)
  x  0.44   business acumen                    (  35 postings, 66% advanced)
  x  0.44   credit risk                        (  46 postings, 54% advanced)
  x  0.44   analytical skills                  ( 155 postings, 61% advanced)
  x  0.44   employee benefits                  (  48 postings, 44% advanced)
  x  0.45   data analysis tools                (  30 postings, 50% advanced)
  x  0.46   regulatory compliance              (  56 postings, 57% advanced)
  x  0.47   risk management framework          (  51 postings, 59% advanced)
  x  0.48   risk management                    ( 195 postings, 62% advanced)
  x  0.49   machine learning                   (  33 postings, 67% advanced)
  x  0.50   accounting                         (  71 postings, 59% advanced)

Coefficient and raw share disagree — conditional effects only, not reported as findings:
  x  2.85   communication                      ( 122 postings, 59% advanced)
  x  2.50   capital markets                    (  55 postings, 55% advanced)
  x  2.03   trend analysis                     (  39 postings, 64% advanced)
  x  0.01   sales                              (  75 postings, 69% advanced)
  x  0.15   operational risk management        (  41 postings, 71% advanced)
  x  1.84   financial analysis                 ( 111 postings, 67% advanced)
  x  1.67   analytics                          (  40 postings, 68% advanced)
  x  0.51   reporting tools                    (  63 postings, 73% advanced)
  x  0.55   career development                 (  43 postings, 70% advanced)
  x  1.26   management                         (  82 postings, 60% advanced)
