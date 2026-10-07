# Pre-Benchmark Prediction Record

## Status

**PRE-BENCHMARK PREDICTIONS — NOT MEASURED RESULTS**

This prediction record must be frozen and committed to the repository before the first official benchmark run. The values below are intentionally specific so that they can later be compared against measured results.

## Candidate Models

| Model | Exact tag | Digest / ID |
|---|---|---|
| Llama 3.2 1B | `llama3.2:1b` | `baf6a787fdff` |
| Gemma 3 4B | `gemma3:4b` | `a2af6cc3eb7f` |
| Mistral 7B Instruct | `mistral:7b-instruct` | `6577803aa9a0` |

## Prediction 1 — Classification Accuracy

Predicted overall accuracy on the frozen golden test set:

| Model | Predicted overall accuracy | Rationale |
|---|---:|---|
| Llama 3.2 1B | **68%** | Expected to be the fastest candidate but to lose more accuracy on ambiguous or multi-issue complaints because it is the smallest model. |
| Gemma 3 4B | **82%** | Expected to provide a stronger balance between classification quality and CPU inference cost. |
| Mistral 7B Instruct | **86%** | Expected to achieve the highest overall accuracy because it is the largest candidate, but at the cost of slower CPU inference. |

These percentages are predictions only and have not been derived from golden-set outputs.

## Prediction 2 — Single-Request Latency

Test condition for later comparison:

- one request at a time;
- no competing benchmark traffic;
- model already downloaded locally;
- CPU-only inference;
- same triage prompt and service path for all candidates.

Predicted typical end-to-end `POST /tickets` latency:

| Model | Predicted single-request latency |
|---|---:|
| Llama 3.2 1B | **2.0 s** |
| Gemma 3 4B | **6.0 s** |
| Mistral 7B Instruct | **10.0 s** |

## Prediction 3 — Expected Bottleneck

**Predicted bottleneck: CPU-bound Ollama model inference.**

Reasoning:

- `POST /tickets` classification is synchronous in the Assignment 1 baseline.
- The service waits for Ollama to finish classification before returning the response.
- There is no caching or application-level queuing optimisation in the baseline.
- Under increasing arrival rate, inference requests are therefore expected to compete for CPU capacity.
- Model inference time is expected to dominate the service's application/database overhead, particularly for the larger candidates.

## Prediction 4 — Hardest Categories

The following category boundaries are predicted to produce the most classification errors:

### Credit reporting vs Debt collection

A complaint can describe an alleged debt, collection activity, and negative credit reporting in the same narrative.

### Bank account or service vs Money transfer or service

Fraud and payment complaints may involve both a bank account and a wire, transfer app, or payment service.

### Consumer loan vs Credit reporting

A consumer may describe an auto, personal, or other consumer loan while primarily disputing how that loan is reported to a credit bureau.

## Expected Overall Ranking

**Accuracy (highest to lowest):**

1. Mistral 7B Instruct
2. Gemma 3 4B
3. Llama 3.2 1B

**Latency / speed (fastest to slowest):**

1. Llama 3.2 1B
2. Gemma 3 4B
3. Mistral 7B Instruct

## Post-Test Comparison

After the golden-set accuracy test and performance tests are completed, the team will compare:

- predicted overall accuracy vs measured overall accuracy;
- predicted model ranking vs measured ranking;
- predicted latency vs measured latency;
- predicted hardest categories vs the actual confusion matrices;
- predicted CPU/Ollama bottleneck vs the observed load/stress-test bottleneck.

The prediction values above must not be edited after the pre-benchmark freeze. Any difference between prediction and measurement should be explained in the final presentation rather than corrected retrospectively.
