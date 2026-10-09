# References and Assumptions

Owner: Bryan Koh Kai Xun

Role: Workload & Requirements Lead

## Source Log

| ID | Source | Publisher | URL | Figure Used | Access Date | Notes |
|---|---|---|---|---|---|---|
| S1 | Consumer Complaint Database | Consumer Financial Protection Bureau | https://www.consumerfinance.gov/data-research/consumer-complaints/ | Dataset origin and complaint domain | 2026-09-20 | Assignment dataset is an extract from this source. |
| S2 | 2024 Consumer Response Annual Report | Consumer Financial Protection Bureau | https://www.consumerfinance.gov/data-research/research-reports/2024-consumer-response-annual-report/ | CFPB received about 3,187,900 complaints in 2024; sent more than 2.8 million complaints to more than 3,600 companies; 98% submitted via website; about 51,000 calls/month. | 2026-09-20 | Primary public source for financial complaint volume. |
| S3 | Consumer Complaint Database - About the database | Consumer Financial Protection Bureau | https://www.consumerfinance.gov/data-research/consumer-complaints/ | Database generally updates daily; CFPB notes complaint volume should be interpreted with company size/market share context. | 2026-09-20 | Used to justify scaling public CFPB volume down to a company workload model. |

## Assumption Log

| ID | Assumption | Reason | Impact |
|---|---|---|---|
| A1 | Use 250 business days/year and 8 business hours/day for staffed triage work. | Public CFPB data gives annual complaint volume, but not the client's staffing calendar. This is a standard conservative business-hours conversion. | Controls average tickets/day and tickets/hour. |
| A2 | Model the client as a larger-than-average company receiving 10x the mean CFPB company-forwarded complaint volume. | CFPB sent about 2,829,400 complaints to more than 3,600 companies in 2024. The simple mean is about 786 complaints/company/year; a 10x multiplier gives a busier desk while remaining traceable to public data. | Sets the baseline ticket arrival rate used for requirements. |
| A3 | Use 70% of tickets during business hours. | Online forms allow after-hours submission, but routing work is likely concentrated when the customer relations desk is staffed. | Increases daytime arrival rate used for tests. |
| A4 | Use a 3x peak-hour multiplier over average business-hour arrival rate. | No public source gives the client's intraday complaint pattern. A 3x multiplier gives the requirement enough headroom for bursty intake. | Sets the peak load requirement. |
| A5 | Use one staff search per five classified tickets. | Staff may search recently routed tickets for follow-up, QA, and escalation, but search is secondary to intake. | Defines mixed endpoint workload. |
| A6 | Accuracy threshold should be high overall and per category because misrouted complaints create operational delay and may affect compliance-sensitive customer handling. | The exact cost of misrouting is unknown, so the threshold is a client-risk judgement. | Controls final recommendation. |

## Citation Notes

Every number shown in Slide 3 or Slide 4 must map back to a row in the source log or assumption log.
