# Bryan Workload Evidence Index

This file tracks the artefacts owned by the Workload & Requirements Lead.

## Scope

Bryan owns the workload model, the requirements derived from it, and the final pass/fail interpretation of measured results against those requirements.

## Tracked Artefacts

| Artefact | Purpose | Status |
|---|---|---|
| `docs/workload_model.md` | Client workload model for Slide 3 | Draft |
| `docs/requirements.md` | Testable performance and accuracy requirements for Slide 4 | Draft |
| `docs/references.md` | Sources and assumptions used by Bryan | Draft |
| `analysis/ticket_length_distribution.csv` | Computed ticket length percentiles from Team 15 rows | Complete |
| `analysis/ticket_length_distribution.md` | Slide-friendly ticket length summary | Complete |
| `analysis/source_label_distribution.csv` | Raw source-label distribution for Team 15 rows | Complete |
| `analysis/workload_calculations.csv` | Workload-to-arrival-rate calculations | Complete |
| `analysis/workload_calculations.md` | Slide-friendly workload calculation summary | Complete |
| `analysis/load_scenarios.csv` | Normal, peak, stretch, and stress load scenarios | Complete |
| `analysis/requirements_traceability.csv` | Requirement thresholds mapped to load condition and evidence | Complete |
| `analysis/requirements_traceability.md` | Slide-friendly requirement traceability table | Complete |
| `docs/workload_requirements_coordination.md` | Coordination checklist for other leads | Complete |
| `docs/workload_requirements_freeze_checklist.md` | Pre-benchmark freeze checklist | Complete |
| `analysis/model_requirement_matrix.csv` | Fill-in matrix for post-test pass/fail interpretation | Template complete |
| `docs/results_interpretation_template.md` | Slide 11 interpretation template | Template complete |
| `docs/slide_3_4_bryan_content.md` | Draft slide content for Bryan's sections | Complete |
| `scripts/analyze_ticket_lengths.py` | Reproducible script for ticket length summaries | Complete |
| `scripts/calculate_workload_rates.py` | Reproducible script for workload-to-load calculations | Complete |

## Local Inputs

The raw assignment context and source extracts are kept in `context/`, which is ignored by Git. Calculations should read from local context files but commit only derived summaries, scripts, and slide-ready evidence.

Current local context used:

- `context/ICT3113_Assignment_1.docx`
- `context/team15_rows.csv`
- `context/plan.md`

## Freeze Rule

Before official benchmark testing starts, the final workload model and requirements must be committed. After that point, only result interpretation should change.
