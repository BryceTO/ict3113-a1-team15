# Results Interpretation Template

Owner: Bryan Koh Kai Xun

Use this after official load, stress, and accuracy tests are complete. Do not change the requirements to fit the results; mark each candidate against the frozen thresholds.

## Requirement Pass/Fail Matrix

| Candidate Model | R1 POST Latency | R2 Throughput | R3 Search Latency | R4 Overall Accuracy | R5 Per-Category Accuracy | Summary Decision |
|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Interpretation Rules

Use these labels:

- Pass: meets the frozen threshold across the required runs.
- Fail: misses the frozen threshold.
- Borderline: technically passes or fails, but run-to-run spread or measurement uncertainty needs discussion.
- Not measured: no valid evidence file exists.

## Evidence Required

For each candidate model, record:

- JMeter `.jtl` files used for p50, p95, p99, throughput, and error rate
- matching service log files
- accuracy output file
- confusion matrix source data
- model tag and digest

## Slide 11 Input

For the final recommendation, Bryan should provide:

- which requirements each model passed or failed
- whether any model satisfies all requirements
- which requirement is the main blocker, if none satisfies all requirements
- whether the recommended model prioritises speed, accuracy, or balanced service quality
- any category-specific accuracy risk that affects routing

## Recommendation Wording Template

```text
Based on the frozen workload model, [MODEL] is the best candidate because it [meets/does not meet] the peak throughput requirement, [meets/does not meet] the latency requirement, and achieves [X]% overall accuracy on the golden set. Its main risk is [CATEGORY/RISK]. We recommend [deploying it / not deploying any candidate yet] because [REASON].
```
