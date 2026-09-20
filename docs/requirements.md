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

These thresholds are derived from the workload model and should be reviewed with the Performance Testing Lead before the official benchmark run. A traceable copy is stored in `analysis/requirements_traceability.md`.

| ID | Area | Requirement | Measurement Source | Status |
|---|---|---|---|---|
| R1 | `POST /tickets` latency | At peak workload of 9 tickets/hour, p95 latency should be <= 60 seconds with error rate <= 1%. | JMeter `.jtl` files and service logs | Ready for team review |
| R2 | Sustained throughput | The system should sustain at least 9 classified tickets/hour under peak workload for the full test duration without unbounded queue growth and with error rate <= 1%. | JMeter throughput, error rate, and service logs | Ready for team review |
| R3 | `GET /search` latency | Under peak mixed workload of 9 `POST /tickets` per hour and 2 `GET /search` requests per hour, p95 search latency should be <= 2 seconds. | JMeter `.jtl` files and service logs | Ready for team review |
| R4 | Overall accuracy | The selected model should achieve at least 75% overall accuracy on the frozen golden set. | Accuracy test output and golden labels | Ready for team review |
| R5 | Per-category accuracy | The selected model should achieve at least 60% accuracy in each category, or any category below threshold must be identified as a routing risk. | Accuracy test output and golden labels | Ready for team review |

## Requirement Rationale To Complete

| Requirement | Rationale Needed |
|---|---|
| R1 | CPU-only local LLM inference may be slow, but complaint routing is asynchronous from the consumer's point of view. A 60-second p95 target is a practical upper bound for first-pass routing without promising real-time chat latency. |
| R2 | Peak complaint intake must be handled without falling behind. The 9 tickets/hour target comes from the workload model's 3x peak-hour estimate. |
| R3 | Staff should be able to find routed tickets while classification load is running. Search is expected to be much lighter than classification and should remain interactive. |
| R4 | Overall automation quality must be high enough to justify replacing manual first-pass routing. 75% is a moderate baseline for a CPU-only model selection exercise and should still expose trade-offs between candidates. |
| R5 | Category-level weakness matters because some teams may receive a disproportionate number of misrouted tickets. A lower per-category threshold allows for difficult categories while still flagging routing risk. |

## Result Interpretation Template

| Candidate Model | R1 Latency | R2 Throughput | R3 Search | R4 Overall Accuracy | R5 Per-Category Accuracy | Decision Notes |
|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Slide 4 Notes

Slide 4 should present the final requirements as client promises, not implementation details. Each requirement needs a number, a load condition, and a short justification from the workload model.
