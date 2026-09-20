# Workload Calculations

## Inputs

| Input | Value |
|---|---:|
| CFPB complaints sent to companies in 2024 | 2,829,400 |
| Companies receiving complaints | 3,600 |
| Client scale factor | 10x mean company volume |
| Business days/year | 250 |
| Business hours/day | 8 |
| Share of tickets during business hours | 70% |
| Peak multiplier | 3x average business-hour rate |
| Search rate | 1 search per 5 classified tickets |

## Derived Workload

| Metric | Formula | Value |
|---|---|---:|
| Mean company-forwarded complaints/year | 2,829,400 / 3,600 | 785.944 |
| Draft client tickets/year | mean company complaints/year * 10 | 7859.444 |
| Tickets/business day | client tickets/year / 250 | 31.438 |
| Business-hours tickets/day | tickets/business day * 70% | 22.006 |
| Average POST /tickets per hour | business-hours tickets/day / 8 | 2.751 |
| Average POST /tickets per minute | average tickets/hour / 60 | 0.046 |
| Peak POST /tickets per hour | average tickets/hour * 3 | 8.252 |
| Peak POST /tickets per minute | peak tickets/hour / 60 | 0.138 |
| Peak GET /search per hour | peak tickets/hour / 5 | 1.65 |
| Peak GET /search per minute | peak searches/hour / 60 | 0.028 |

## Load Scenarios

| Scenario | Purpose | POST/hour | POST/minute | Search/hour | Endpoint mix |
|---|---|---:|---:|---:|---|
| normal | Typical complaint intake | 3 | 0.05 | 0 | Mostly POST /tickets |
| peak | Main requirement condition | 9 | 0.15 | 2 | POST /tickets plus GET /search |
| stretch | Headroom demonstration | 60 | 1.0 | 12 | Same endpoint mix as peak |
| stress | Find system limit | TBD | TBD | TBD | Increase POST /tickets until failure or unbounded latency |
