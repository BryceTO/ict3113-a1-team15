# Workload Model

Owner: Bryan Koh Kai Xun  
Role: Workload & Requirements Lead

## Client Scenario

The client is a financial services company with a customer relations desk that receives complaint tickets. Today, each ticket is read and routed by a human. The proposed system classifies each incoming ticket into one of seven complaint categories so it can be routed to the correct team.

The system must run on infrastructure controlled by the client. Public model APIs are not allowed because complaint narratives may contain sensitive financial information. Model inference is CPU-only through Ollama.

## Workload Questions

The workload model must estimate:

- incoming complaint ticket volume
- normal and peak `POST /tickets` arrival rates
- staff-side `GET /search` usage
- peak and non-peak periods
- expected complaint narrative length distribution

## Dataset Context

Team 15 uses the assignment extract rows 15000 to 15999.

Local dataset summary from `context/team15_rows.csv`:

| Field | Value |
|---|---:|
| Total tickets | 1,000 |
| Minimum narrative length | 201 characters |
| Mean narrative length | about 879 characters |
| Maximum narrative length | 1,989 characters |

Raw source label distribution:

| Source label | Count |
|---|---:|
| Credit reporting | 159 |
| Mortgage | 151 |
| Credit card | 149 |
| Money transfer or service | 148 |
| Debt collection | 134 |
| Bank account or service | 132 |
| Consumer loan | 127 |

These raw source labels are useful for describing the dataset slice, but they are noisy and must not replace the team-adjudicated golden labels for accuracy measurement.

## Modelling Units

The workload model will express ticket volume as:

- tickets per year
- tickets per business day
- tickets per business hour
- tickets per minute

JMeter test conditions should be expressed as controlled open-loop arrival rates.

## Assumptions To Resolve

| ID | Assumption | Status |
|---|---|---|
| A1 | 250 business days/year and 8 business hours/day | Draft |
| A2 | Client workload model uses 10x mean CFPB company-forwarded complaint volume | Draft |
| A3 | 70% of tickets arrive during business hours | Draft |
| A4 | Peak hour is 3x average business-hour rate | Draft |
| A5 | Staff make one search per five classified tickets | Draft |
| A6 | Acceptable misrouting risk is represented by overall and per-category accuracy thresholds | Pending team decision |

## Public Workload Evidence

The strongest public source for this workload is the CFPB's 2024 Consumer Response Annual Report. CFPB reported about 3,187,900 complaints received in 2024, with more than 2.8 million sent to more than 3,600 companies for review and response. CFPB also reported that 98% of complaints were submitted through its website, supporting the assignment's assumption that tickets arrive digitally one at a time.

For a company-level model, this plan uses the complaints sent to companies rather than all complaints received:

```text
Mean company-forwarded complaints/year = 2,829,400 / 3,600
                                      ~= 786 complaints/company/year
```

The assignment client is described as having a steady complaint stream. To avoid modelling an unrealistically quiet average company, Bryan's draft model treats the client as a busier financial services company at 10x this simple mean:

```text
Draft client annual tickets = 786 * 10
                            ~= 7,860 tickets/year
```

This is an assumption, not a direct public figure. It should be presented as a scaled workload model derived from CFPB volume.

## Draft Workload Calculations

Using 7,860 tickets/year:

| Metric | Formula | Draft Value |
|---|---|---:|
| Tickets/business day | 7,860 / 250 | 31.4 tickets/day |
| Tickets during business hours/day | 31.4 * 70% | 22.0 tickets/day |
| Average business-hour intake | 22.0 / 8 | 2.75 tickets/hour |
| Average business-hour intake | 2.75 / 60 | 0.046 tickets/minute |
| Peak intake | 2.75 * 3 | 8.25 tickets/hour |
| Peak intake | 8.25 / 60 | 0.138 tickets/minute |
| Staff search rate at peak | 8.25 / 5 | 1.65 searches/hour |

The raw peak rate is low because real financial complaints are usually sparse compared with web traffic. For performance testing, the team should still test higher stretch and stress arrival rates to find the system limit, but the formal client requirement should remain tied to the workload model.

## Draft Load Scenarios

| Scenario | Purpose | Arrival Rate | Endpoint Mix | Status |
|---|---|---:|---|---|
| Normal load | Typical complaint intake | 3 `POST /tickets` per hour | Mostly `POST /tickets` | Draft |
| Peak load | Main requirement condition | 9 `POST /tickets` per hour plus 2 searches/hour | `POST /tickets` plus `GET /search` | Draft |
| Stretch load | Demonstrate headroom above modelled peak | 60 `POST /tickets` per hour plus 12 searches/hour | Same mix as peak | Draft, coordinate with Performance Lead |
| Stress load | Find system limit | Increase until latency grows without bound or errors rise materially | Increased `POST /tickets` | Performance Lead to finalise |

## Slide 3 Notes

Slide 3 should show a compact workload story:

- client ticket volume estimate
- normal and peak arrival rates
- search workload assumption
- ticket length distribution from Team 15 rows
- which figures are sourced versus estimated
