# Bryan's Golden-Set Labelling Plan

## Scope

Bryan is Person B in the team plan. The golden set contains 175 Team 15 tickets; each ticket needs two independent labels. Bryan contributes **70 first-pass labels**. Yuhao (Person E) owns ticket selection, assignment, the labelling protocol, comparison, agreement calculation, and the final golden set.

| Pair | Shared tickets Bryan labels |
|---|---:|
| Bryan + Bryce (A + B) | 18 |
| Bryan + Liando (B + C) | 18 |
| Bryan + ZD (B + D) | 17 |
| Bryan + Yuhao (B + E) | 17 |
| **Total** | **70** |

This is separate from Bryan's workload and requirements deliverables.

## Phase 1 - Get the labelling packet

- [ ] Ask Yuhao for the frozen list of Bryan's 70 assigned row IDs, with the four pair groups above. Confirm each ID is unique and within Team 15 rows 15000-15999.
- [ ] Get the team's current labelling protocol, exact seven permitted category names, tie-breaking rules, and label-sheet location/format.
- [ ] Confirm that the view used for annotation shows the ticket narrative and row ID but hides `source_label` and model predictions. Source labels are noisy and are only used to build the sample.
- [ ] Agree on a completion date and how to return the independent sheet to Yuhao.

**Exit:** Bryan has a 70-row assignment and a shared protocol. Do not invent ticket IDs or start from an unassigned sample.

## Phase 2 - Label independently

- [ ] Read each assigned narrative and choose exactly one of the seven categories according to the protocol.
- [ ] Record the row ID, chosen category, and a short rationale or ambiguity note where useful. Use Yuhao's sheet format if provided.
- [ ] Work without viewing the other annotator's answer, the raw `source_label`, or candidate-model output; do not discuss individual tickets before both labels are recorded.
- [ ] If a case is unclear, record the uncertainty and the closest protocol rule. Keep the initial label unchanged until the comparison phase.
- [ ] Check that all 70 assigned IDs have exactly one Bryan label, valid category spelling, and no extra IDs.

**Exit:** One complete, timestamped independent label sheet for Bryan's 70 tickets.

## Phase 3 - Hand off to Yuhao

- [ ] Share or commit the independent sheet in the agreed location, then send Yuhao its path and the count: 18/18/17/17 across the four pair groups.
- [ ] Keep the original independent answers available for the agreement calculation. Corrections should be traceable, not silently overwritten.
- [ ] Tell Yuhao which IDs have ambiguity notes so they can be included in the disagreement review.

**Exit:** Yuhao can match Bryan's sheet against the four partners' sheets by row ID without guessing which version is original.

## Phase 4 - Resolve disagreements

- [ ] Wait for Yuhao's disagreement list; review only tickets involving Bryan.
- [ ] Discuss those cases with the paired annotator using the narrative and protocol. Record the final category, reason, participants, and any protocol clarification.
- [ ] Preserve Bryan's original independent label separately from the adjudicated final label so agreement remains measurable.
- [ ] Confirm with Yuhao when all Bryan-involved disagreements are resolved.

**Exit:** Bryan's assigned tickets have two recorded first-pass labels and, where needed, a documented final decision.

## Phase 5 - Freeze and handoff check

- [ ] Ask Yuhao to confirm the complete 175-ticket golden set, independent sheets, disagreement log, protocol revisions, and agreement statistic are committed before official benchmarking.
- [ ] Confirm that accuracy comparisons use adjudicated golden labels, not the CSV's `source_label` values.
- [ ] Link the frozen golden-set commit in Bryan's requirements handoff so R4/R5 can be judged against the correct labels.

**Done when:** Bryan's 70 labels are delivered, his disagreements are resolved, and Yuhao confirms the golden-set freeze. Labelling is not complete just because this plan exists.
