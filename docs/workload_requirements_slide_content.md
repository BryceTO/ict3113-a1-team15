# Bryan Slide Content Draft

Owner: Bryan Koh Kai Xun

## Slide 3 - Workload Model

### Core Message

The client workload is low-volume compared with ordinary web traffic, but each classification is expensive because `POST /tickets` waits synchronously for CPU-only local LLM inference.

### Suggested Slide Table

| Workload Element | Value | Basis |
|---|---:|---|
| CFPB complaints sent to companies in 2024 | about 2.8 million | CFPB 2024 Consumer Response Annual Report |
| Companies receiving CFPB complaints | more than 3,600 | CFPB 2024 Consumer Response Annual Report |
| Mean company-forwarded complaints/year | about 786 | 2,829,400 / 3,600 |
| Draft client scale | 10x mean company volume | Conservative larger-company assumption |
| Draft client tickets/year | about 7,860 | 786 * 10 |
| Normal intake | 3 tickets/hour | Workload calculation rounded from average business-hour rate |
| Peak intake | 9 tickets/hour | 3x average business-hour rate |
| Staff search workload at peak | 2 searches/hour | 1 search per 5 classified tickets |

### Ticket Length Summary

| Metric | Characters | Words | Estimated Tokens |
|---|---:|---:|---:|
| Median | 795 | 140 | 199 |
| p95 | 1,750 | 311 | 438 |
| Max | 1,989 | 374 | 498 |

### Speaker Notes

- Public CFPB data gives market-scale complaint volume, not this exact client's private workload.
- The 10x company-average multiplier is an explicit assumption to model a busier financial services desk.
- The formal peak requirement is intentionally tied to realistic complaint volume, while stretch and stress tests still explore system limits.
- Raw source labels are noisy; they describe the dataset slice only and are not used as golden labels.

## Slide 4 - Performance and Accuracy Requirements

### Suggested Slide Table

| ID | Requirement | Threshold | Load Condition |
|---|---|---:|---|
| R1 | `POST /tickets` p95 latency | <= 60 seconds, error rate <= 1% | 9 tickets/hour |
| R2 | Sustained throughput | >= 9 classified tickets/hour | Peak load test duration |
| R3 | `GET /search` p95 latency | <= 2 seconds | 9 tickets/hour + 2 searches/hour |
| R4 | Overall accuracy | >= 75% | Frozen golden set |
| R5 | Per-category accuracy | >= 60% per category, otherwise flag routing risk | Frozen golden set |

### Justification

- Throughput target comes from the modelled peak complaint intake.
- Latency target allows CPU-only local inference but prevents the intake queue from becoming operationally useless.
- Search target keeps staff lookup interactive during classification load.
- Accuracy targets reflect first-pass routing risk: overall accuracy matters, but per-category weakness can overload or misroute a specific team.

## Slide 11 Input - Recommendation Defence

Use `analysis/model_requirement_matrix.csv` after testing to answer:

- Which model passes the peak workload requirements?
- Which model has the best accuracy without failing latency or throughput?
- Does any model fail a specific category badly enough to create routing risk?
- If no model meets all requirements, recommend that honestly and explain the main blocker.

## Slide 12 References Input

Use these sources for Bryan's part:

- Consumer Financial Protection Bureau. Consumer Complaint Database. https://www.consumerfinance.gov/data-research/consumer-complaints/
- Consumer Financial Protection Bureau. 2024 Consumer Response Annual Report. https://www.consumerfinance.gov/data-research/research-reports/2024-consumer-response-annual-report/

Include access date: 20 September 2026.
