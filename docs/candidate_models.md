# Candidate Models

## Purpose

The candidate set was selected for the ICT3113 Assignment 1 ticket-classification service. The client requires local, CPU-only inference on commodity hardware, so the set intentionally spans small, medium, and larger models to expose the trade-off between classification accuracy and inference performance.

All three models were pulled and verified locally using Ollama 0.40.0 on the team's model host.

## Test Host

- CPU: Intel Core Ultra 7 155H
- RAM: 16 GB (15.6 GB usable)
- Operating system: Windows 64-bit
- Ollama version: 0.40.0
- Inference constraint: CPU-only for official testing

## Candidate Set

| Model | Exact Ollama tag | Digest | Local size | Size class | Licence | Selection rationale |
|---|---|---|---:|---|---|---|
| Llama 3.2 1B | `llama3.2:1b` | `baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878` | 1.3 GB | Small | Llama 3.2 Community License Agreement | Smallest baseline. Selected to represent a low-resource, speed-first CPU model and show the lower end of the accuracy/performance trade-off. |
| Gemma 3 4B | `gemma3:4b` | `a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a` | 3.3 GB | Medium | Gemma Terms of Use | Mid-sized candidate. Selected to represent a balance between classification quality and CPU inference cost. |
| Mistral 7B Instruct | `mistral:7b-instruct` | `6577803aa9a036369e481d648a2baebb381ebc6e897f2bb9a766a2aa7bfbc1cf` | 4.4 GB | Larger | Apache License 2.0 | Largest candidate. Selected to test whether a larger instruction-tuned model provides enough accuracy improvement to justify higher CPU latency and lower throughput. |

## Why These Three Models

The set spans approximately 1B, 4B, and 7B parameters and uses three different model families. This creates a clear small/medium/large comparison while keeping the total benchmarking workload manageable.

The candidate set supports two useful comparisons:

1. **Model-size trade-off:** determine whether larger models improve ticket-classification accuracy enough to justify slower CPU inference.
2. **Model-family trade-off:** compare three different instruction-model families rather than testing only different sizes from one family.

The largest model is limited to the 7B class because the available host has 16 GB RAM and must also run Ollama, the triage service, and the operating system.

## Sanity Check

Before official benchmarking, each candidate was given three synthetic, non-golden complaints representing:

- Credit reporting
- Mortgage
- Money transfer or service

All three candidates returned the expected category for all three examples.

This was only a **sanity/compatibility check** to confirm that the models run and can follow the seven-class prompt. It is **not** reported as classification accuracy.

## Reproducibility

The final report should use the exact model tags and local IDs/digests recorded above. If a model is re-pulled and its ID changes before official testing, this document must be updated before the benchmark freeze so that the recorded version matches the version actually tested.
