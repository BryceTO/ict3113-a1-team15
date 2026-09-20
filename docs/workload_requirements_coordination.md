# Workload & Requirements Coordination Checklist

Owner: Bryan Koh Kai Xun

Use this checklist before the official benchmark run. The goal is to make sure the workload model and requirements can be measured by the team's actual service, JMeter plans, and accuracy scripts.

## Service Lead Check

| Item | Expected Answer | Status |
|---|---|---|
| `POST /tickets` endpoint exists | Accepts one narrative, waits for classification, stores result, returns category | Pending |
| `GET /search` endpoint exists | Searches stored ticket narratives by text query | Pending |
| `GET /stats` endpoint exists | Returns stored ticket counts by category | Pending |
| Request logs include endpoint | Required for reconciling JMeter results | Pending |
| Request logs include latency | Required for checking p95/p99 against JMeter | Pending |
| Request logs include model name | Required for per-candidate traceability | Pending |
| Request logs include status/error | Required for error-rate checks | Pending |

## Performance Testing Lead Check

| Item | Bryan Requirement Dependency | Status |
|---|---|---|
| Open-loop JMeter plan | Required by assignment and throughput evidence | Pending |
| CSV feeder uses Team 15 rows | Required by assignment | Pending |
| Peak load scenario: 9 `POST /tickets`/hour + 2 `GET /search`/hour | Measures R1, R2, R3 | Pending |
| Stretch load scenario: 60 `POST /tickets`/hour + 12 `GET /search`/hour | Shows headroom beyond workload model | Pending |
| Stress test increases load until limit is found | Required by assignment | Pending |
| Three runs per candidate/configuration | Required by assignment | Pending |
| Reports p50, p95, p99, achieved throughput, error rate | Required by assignment and requirements | Pending |

## Model & Accuracy Lead Check

| Item | Bryan Requirement Dependency | Status |
|---|---|---|
| Candidate model tags and digests pinned | Needed before official tests | Pending |
| Predictions recorded before official benchmark | Assignment freeze requirement | Pending |
| Accuracy script compares predictions to adjudicated golden labels | Measures R4 and R5 | Pending |
| Overall accuracy reported per model | Measures R4 | Pending |
| Per-category accuracy reported per model | Measures R5 | Pending |
| Confusion matrices produced | Supports recommendation defence | Pending |

## Golden Set & Integration Lead Check

| Item | Bryan Requirement Dependency | Status |
|---|---|---|
| Golden set frozen before official tests | Required for valid accuracy requirements | Pending |
| Adjudicated labels, not raw source labels, used for accuracy | Measures R4 and R5 correctly | Pending |
| Category distribution of golden set available | Needed to interpret per-category accuracy | Pending |
| Agreement statistic available | Supports Slide 6 and confidence in R4/R5 | Pending |

## Team Decision Needed

| Decision | Bryan Recommendation | Final Team Decision |
|---|---|---|
| Use 10x mean CFPB company volume as client workload | Yes, gives a busier but source-traceable desk | Pending |
| Use 9 tickets/hour as formal peak throughput requirement | Yes, rounded from modelled 8.25 tickets/hour | Pending |
| Include stretch scenario at 60 tickets/hour | Yes, useful to show headroom and compare models | Pending |
| Overall accuracy threshold | 75% | Pending |
| Per-category accuracy threshold | 60% | Pending |

## Sign-Off Rule

When all pending items that affect Bryan's requirements are resolved, update this file and commit the frozen version before the first official benchmark run.
