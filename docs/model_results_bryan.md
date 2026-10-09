# Bryan's Model Requirement Comparison

Evidence snapshot: `main@2f6745d` (9 October 2026). The thresholds below come from the pre-test draft in `docs/requirements.md` on Bryan's branch. That document has not been marked formally frozen; do not describe the results as a test of a signed-off freeze until the team confirms its status.

## Requirement Conditions

| ID | Threshold | Interpretation |
|---|---|---|
| R1 | `POST /tickets` p95 <= 60 s and error rate <= 1% at 9 tickets/h | The available 60/h and 180/h runs are stronger-load evidence, not a direct 9/h measurement. |
| R2 | >= 9 classified tickets/h without unbounded backlog and error rate <= 1% | Use achieved throughput and backlog timelines from the valid load runs. |
| R3 | `GET /search` p95 <= 2 s with 9 tickets/h and 2 searches/h | Available mixed-load runs use 12 or 36 searches/h. Search p95 has only 4 samples per 60/h run and 12 per 180/h run. |
| R4 | Overall accuracy >= 75% on 175 adjudicated tickets | Count backend errors as incorrect. Use `end_to_end_correct_percent`, not accuracy restricted to successful responses. |
| R5 | Each category >= 60% or a lower-scoring category must be flagged as a routing risk | Use the full golden-category denominator; a backend error is not excluded from the category. |

## Measured Comparison

| Model | R1-R3 load evidence | R4 end-to-end | R5 below 60% | Recommendation |
|---|---|---:|---|---|
| `llama3.2:1b` | Valid 60/h and 180/h runs meet latency, throughput and error targets | 34/175 = 19.43%; fail | 6 of 7 categories | Reject |
| `gemma3:4b` | Valid 60/h and 180/h runs meet latency, throughput and error targets | 134/175 = 76.57%; pass | Consumer loan: 3/15 = 20.00% | Guarded pilot only, with Consumer loan review |
| `mistral:7b-instruct` | Valid 60/h and 180/h runs meet latency, throughput and error targets | 120/175 = 68.57%; fail; 24 backend errors | Consumer loan: 8/15 = 53.33%; Money transfer or service: 13/28 = 46.43% | Reject |

Across valid runs, the worst `POST /tickets` p95 was 7.854 s for Llama, 14.958 s for Gemma, and 49.840 s for Mistral. Worst search p95 was 0.777 s, 0.237 s, and 1.074 s respectively. All valid 60/h and 180/h load runs had 0% request errors, achieved at least 59.8 classified tickets/h, and ended with no backlog. The 60/h searches have 4 samples per run and the 180/h searches 12, so R3 is supported but measured imprecisely. Llama's first 60/h run failed JMeter/service-log reconciliation and is excluded; runs 2-4 provide the three valid repeats.

Mistral's successful-response accuracy was 79.47%, but 24 of 175 requests failed. Its correct outcomes across the entire golden set were 120/175 = 68.57%, which is the relevant R4 measure. The published per-category CSV divides by successful requests only; the R5 figures above divide by all tickets in each golden category.

## Slide 11 Recommendation Input

Gemma 3 4B is the strongest candidate because it is the only model above the 75% end-to-end accuracy threshold while its valid load runs stay within the latency and throughput targets. It is **not** a clean seven-category pass: Consumer loan accuracy is 20% (3/15). Recommend a guarded pilot only if Consumer loan tickets receive manual review and the team accepts that routing risk. Otherwise, report that no candidate fully meets the category target. The inference from 60/h and 180/h to the modelled 9/h peak, and the small search sample count, must be stated rather than hidden.

Evidence: `results/summary/load_configs.csv`, `results/summary/load_runs.csv`, `results/summary/timeline/`, `results/accuracy/accuracy_summary.csv`, `results/accuracy/per_category_accuracy.csv`, `results/accuracy/confusion_*.csv`, and `golden_set/golden_set.csv` at `main@2f6745d`.
