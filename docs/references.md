# References and Assumptions

Owner: Bryan Koh Kai Xun  
Role: Workload & Requirements Lead

## Source Log

| ID | Source | Publisher | URL | Figure Used | Access Date | Notes |
|---|---|---|---|---|---|---|
| S1 | Consumer Complaint Database | Consumer Financial Protection Bureau | https://www.consumerfinance.gov/data-research/consumer-complaints/ | Dataset origin and complaint domain | 2026-09-20 | Assignment dataset is an extract from this source. |

## Assumption Log

| ID | Assumption | Reason | Impact |
|---|---|---|---|
| A1 | TBD business-hour model | Needed to convert annual or daily complaint volume into hourly arrival rate. | Controls JMeter arrival rates. |
| A2 | TBD peak multiplier | Needed because requirements must cater for peak workload if peak periods exist. | Controls peak load requirement. |
| A3 | TBD search rate | Needed to model `GET /search` under staff usage. | Controls mixed endpoint test. |
| A4 | TBD accuracy threshold | Needed to decide whether model routing is operationally acceptable. | Controls final recommendation. |

## Citation Notes

Every number shown in Slide 3 or Slide 4 must map back to a row in the source log or assumption log.
