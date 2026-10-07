# Leakage check

## Train / validation / test split

- train: 201801 to 202008 (15178 reports)
- val: 202009 to 202104 (3428 reports)
- test: 202105 to 202112 (3027 reports)
- train ends before val starts: True (share a month: False)
- val ends before test starts: True (share a month: False)
- train/val shared ACNs: 0, shared identical texts: 0
- train/test shared ACNs: 0, shared identical texts: 0
- val/test shared ACNs: 0, shared identical texts: 0

## Monthly-share tracking, 2019-01 to 2021-12 (36 months)

- median correlation, random 5-fold CV (used before): 0.67
- median correlation, forward in time (trained only on earlier years): 0.68
- median mean absolute error of the monthly share, random CV: 0.0075
- median mean absolute error of the monthly share, forward: 0.0097

| label                                                            |   mean_share |   corr_random_cv |   corr_forward |   mae_random_cv |   mae_forward |
|:-----------------------------------------------------------------|-------------:|-----------------:|---------------:|----------------:|--------------:|
| Deviation / Discrepancy - Procedural Published Material / Policy |        0.577 |            0.556 |          0.443 |           0.055 |         0.074 |
| Aircraft Equipment Problem Less Severe                           |        0.203 |            0.701 |          0.722 |           0.033 |         0.05  |
| Deviation / Discrepancy - Procedural Clearance                   |        0.199 |            0.29  |          0.413 |           0.035 |         0.054 |
| ATC Issue All Types                                              |        0.186 |            0.86  |          0.859 |           0.014 |         0.014 |
| Aircraft Equipment Problem Critical                              |        0.162 |            0.892 |          0.845 |           0.034 |         0.057 |
| Deviation / Discrepancy - Procedural FAR                         |        0.105 |            0.313 |          0.361 |           0.05  |         0.08  |
| Inflight Event / Encounter Weather / Turbulence                  |        0.088 |            0.759 |          0.697 |           0.018 |         0.021 |
| Conflict NMAC                                                    |        0.08  |            0.945 |          0.939 |           0.009 |         0.008 |
| Inflight Event / Encounter CFTT / CFIT                           |        0.077 |            0.917 |          0.918 |           0.008 |         0.011 |
| Deviation - Track / Heading All Types                            |        0.072 |            0.606 |          0.721 |           0.017 |         0.022 |
| Flight Deck / Cabin / Aircraft Event Smoke / Fire / Fumes / Odor |        0.06  |            0.993 |          0.983 |           0.006 |         0.009 |
| Conflict Ground Conflict                                         |        0.052 |            0.922 |          0.924 |           0.006 |         0.01  |
