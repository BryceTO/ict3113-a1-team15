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
| A1 | Business hours used for converting daily complaint volume into hourly arrival rate | Pending source or team decision |
| A2 | Percentage of complaints arriving during business hours | Pending source or conservative estimate |
| A3 | Peak-hour multiplier over average business-hour rate | Pending source or conservative estimate |
| A4 | Staff search rate per classified ticket | Pending source or conservative estimate |
| A5 | Acceptable operational risk for misrouted complaints | Pending team decision |

## Draft Load Scenarios

| Scenario | Purpose | Arrival Rate | Endpoint Mix | Status |
|---|---|---:|---|---|
| Normal load | Typical complaint intake | TBD | Mostly `POST /tickets` | Pending research |
| Peak load | Main requirement condition | TBD | `POST /tickets` plus `GET /search` | Pending research |
| Stress load | Find system limit | TBD | Increased `POST /tickets` | Performance Lead to finalise |

## Slide 3 Notes

Slide 3 should show a compact workload story:

- client ticket volume estimate
- normal and peak arrival rates
- search workload assumption
- ticket length distribution from Team 15 rows
- which figures are sourced versus estimated
