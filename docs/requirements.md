# Performance and Accuracy Requirements

Owner: Bryan Koh Kai Xun  
Role: Workload & Requirements Lead

## Requirement Rules

Each requirement must be testable and tied to the workload model. A valid requirement includes:

- endpoint or result being measured
- numeric threshold
- percentile, where relevant
- load condition
- measurement source
- justification

The final thresholds must be frozen before official benchmark testing begins.

## Draft Requirements

These are placeholders until the workload model is finalised.

| ID | Area | Requirement | Measurement Source | Status |
|---|---|---|---|---|
| R1 | `POST /tickets` latency | At peak workload of X tickets/minute, p95 latency should be <= Y seconds with error rate <= Z%. | JMeter `.jtl` files and service logs | Pending thresholds |
| R2 | Sustained throughput | The system should sustain at least X classified tickets/hour under peak workload without unbounded queue growth and with error rate <= Z%. | JMeter throughput, error rate, and service logs | Pending thresholds |
| R3 | `GET /search` latency | Under mixed workload of X% `POST /tickets` and Y% `GET /search`, p95 search latency should be <= Z seconds. | JMeter `.jtl` files and service logs | Pending endpoint mix |
| R4 | Overall accuracy | The selected model should achieve at least X% overall accuracy on the frozen golden set. | Accuracy test output and golden labels | Pending threshold |
| R5 | Per-category accuracy | The selected model should achieve at least X% accuracy in each category, or any category below threshold must be identified as a routing risk. | Accuracy test output and golden labels | Pending threshold |

## Requirement Rationale To Complete

| Requirement | Rationale Needed |
|---|---|
| R1 | Human-facing complaint intake should not be delayed beyond an acceptable routing wait. |
| R2 | Peak complaint intake must be handled without falling behind. |
| R3 | Staff should be able to find routed tickets while classification load is running. |
| R4 | Overall automation quality must be high enough to justify replacing manual first-pass routing. |
| R5 | Category-level weakness matters because some teams may receive a disproportionate number of misrouted tickets. |

## Result Interpretation Template

| Candidate Model | R1 Latency | R2 Throughput | R3 Search | R4 Overall Accuracy | R5 Per-Category Accuracy | Decision Notes |
|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Slide 4 Notes

Slide 4 should present the final requirements as client promises, not implementation details. Each requirement needs a number, a load condition, and a short justification from the workload model.
