# Bryan Slide Handoff

Review deck: `slides/team15_bryan_draft.pptx`. This is a copy of the team deck supplied on 9 October 2026, not a replacement for Yuhao's master presentation. Rebuild it from the supplied source with `scripts/build_bryan_slides.ps1` and separate `-Source`, `-Output`, and optional `-PreviewDir` paths.

## Slides Updated

- Slide 3: modelled annual, normal and peak ticket volume; peak search activity; narrative length. Source and assumptions are named on the slide.
- Slide 4: removed unrelated template text and presented R1-R5. The modelled client peak remains 9 tickets/hour; 60/h and 180/h are measured headroom scenarios.
- Slide 11: compared pre-test predictions with end-to-end measured accuracy, showed requirement outcomes, and recommended only a supervised Gemma 3 4B pilot with human approval of every proposed route.
- Slide 12: added Bryan's workload references and repository evidence. Other owners can add their references in the final deck.

The text on Slides 1, 2 and 5-10 was not changed. This deck is Bryan's contribution for Yuhao to review and integrate; it is not a team-approved final recommendation.

## Evidence and Review Points

- Bryan's thresholds: `docs/requirements.md` on this branch, drafted before testing but not marked formally frozen.
- Per-model assessment and caveats: `docs/model_results_bryan.md` and `analysis/model_requirement_matrix.csv`.
- Test and accuracy snapshot: `main@2f6745d`, especially `results/summary/load_configs.csv`, `results/summary/load_runs.csv`, `results/accuracy/accuracy_summary.csv`, and `results/accuracy/per_category_accuracy.csv`.
- Golden set: `main@2f6745d:golden_set/golden_set.csv`.
- The measured 60/h and 180/h runs support, but do not directly measure, latency at the modelled 9/h peak. Search p95 uses only 4 or 12 requests per run.
- Mistral's 79.47% successful-response accuracy excludes 24 backend failures; R4 uses 120/175 = 68.57% end-to-end.
- Gemma meets R4 at 134/175 = 76.57%, but Consumer loan is 3/15 = 20%. Reviewing only model-predicted Consumer loan tickets would miss true Consumer loan cases that it misroutes. A supervised pilot therefore requires human approval of every classification until the weakness is addressed.

Yuhao and the other leads should confirm requirement-freeze status, the final recommendation wording, and complete the shared reference slide before submitting the deck.
