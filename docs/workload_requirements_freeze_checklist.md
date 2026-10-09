# Workload & Requirements Freeze Checklist

Owner: Bryan Koh Kai Xun

This checklist should be completed before the team's first official benchmark run. Once frozen, the workload model and requirements should not be changed based on benchmark results.

## Freeze Gate

| Item | Evidence File | Status |
|---|---|---|
| Workload source figures recorded | `docs/references.md` | Ready for review |
| Assumptions recorded and labelled | `docs/references.md` | Ready for review |
| Workload calculations reproducible | `scripts/calculate_workload_rates.py`, `analysis/workload_calculations.md` | Complete |
| Ticket length distribution reproducible | `scripts/analyze_ticket_lengths.py`, `analysis/ticket_length_distribution.md` | Complete |
| Normal, peak, stretch, and stress scenarios defined | `analysis/load_scenarios.csv` | Complete |
| Response time requirement defined | `docs/requirements.md`, `analysis/requirements_traceability.md` | Ready for review |
| Throughput requirement defined | `docs/requirements.md`, `analysis/requirements_traceability.md` | Ready for review |
| Search latency requirement defined | `docs/requirements.md`, `analysis/requirements_traceability.md` | Ready for review |
| Overall accuracy requirement defined | `docs/requirements.md`, `analysis/requirements_traceability.md` | Ready for review |
| Per-category accuracy requirement defined | `docs/requirements.md`, `analysis/requirements_traceability.md` | Ready for review |
| Performance Testing Lead confirms JMeter can measure R1-R3 | `docs/workload_requirements_coordination.md` | Pending team confirmation |
| Model & Accuracy Lead confirms accuracy process can measure R4-R5 | `docs/workload_requirements_coordination.md` | Pending team confirmation |
| Golden Set Lead confirms final labels are frozen | Team golden-set artefacts | Pending team confirmation |

## Freeze Statement Template

Use this text in the commit or team chat when the requirements are accepted:

```text
Bryan's workload model and requirements are frozen for Assignment 1 benchmarking.
Official benchmark results should be compared against these committed requirements.
Any later changes must be marked as result interpretation, not revised requirements.
```

## Current Freeze Status

Not frozen yet. The workload and requirements are ready for team review, but final freeze depends on JMeter, model accuracy, and golden-set confirmation from the other leads.
