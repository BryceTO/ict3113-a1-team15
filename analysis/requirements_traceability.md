# Requirements Traceability

These requirements are derived from the workload model and should be frozen before the first official benchmark run.

| ID | Area | Load Condition | Threshold | Measurement Source | Justification | Status |
|---|---|---|---|---|---|---|
| R1 | `POST /tickets` latency | Peak load: 9 `POST /tickets` per hour | p95 latency <= 60 seconds and error rate <= 1% | JMeter `.jtl` files plus service request logs | CPU-only LLM classification is not real-time but should route complaints within a practical first-pass wait. | Ready for team review |
| R2 | Sustained throughput | Peak load: 9 `POST /tickets` per hour | Sustain 9 classified tickets/hour for full test duration without unbounded queue growth and error rate <= 1% | JMeter throughput/error rate plus service request logs | Peak intake must be handled without falling behind. | Ready for team review |
| R3 | `GET /search` latency | Mixed peak: 9 `POST /tickets` per hour plus 2 `GET /search` per hour | p95 search latency <= 2 seconds | JMeter `.jtl` files plus service request logs | Staff search should remain interactive while classification load is running. | Ready for team review |
| R4 | Overall accuracy | Frozen golden set | Overall accuracy >= 75% | Accuracy test outputs compared with adjudicated golden labels | Automation must be reliable enough to justify first-pass routing. | Ready for team review |
| R5 | Per-category accuracy | Frozen golden set | Each category accuracy >= 60% or flagged as routing risk | Accuracy test outputs and per-category confusion matrix | Overall accuracy can hide category-specific misrouting risk. | Ready for team review |

## Freeze Note

Once the team accepts these requirements, commit them before official benchmark testing starts. After that, changes should be limited to measured pass/fail interpretation.
