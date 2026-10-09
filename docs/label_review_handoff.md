# Bryan Labelling Handoff

## Draft labels for Bryan's review

The AI-assisted draft is `data/labels/label_review_draft.csv`. It contains 70 row IDs, one suggested category per row, pair group, and short notes where the product or routing could be debated. It is **not yet Bryan's independently verified human label sheet**. Narratives and `source_label` values are omitted from the draft; use `context/team15_rows.csv` to retrieve narratives by row ID.

The assigned IDs were **inferred**, not supplied as a separate Yuhao packet. The shared team plan allocates the first 175 Team 15 rows in consecutive pair blocks. Bryce's sheet confirms `A+B` = 15000-15017, `E+A` = 15072-15089, `A+C` = 15090-15106, and `A+D` = 15107-15123. Continuing those blocks gives Bryan `B+C` = 15018-15035, `B+D` = 15124-15140, and `B+E` = 15141-15157. Yuhao should confirm this allocation against the master sheet before treating the labels as final input.

Bryan confirmed the only permitted labels are `Credit reporting`, `Debt collection`, `Mortgage`, `Credit card`, `Bank account or service`, `Consumer loan`, and `Money transfer or service`. All 70 draft labels use these exact names. There is still no team tie-breaking protocol in this checkout. Bryan should review every narrative and suggested category himself against Yuhao's protocol, edit decisions where needed, and then submit his verified independent sheet. Student-loan cases were placed under `Consumer loan` because the seven-category taxonomy has no student-loan class; this rule needs protocol confirmation.

## For Yuhao

1. Confirm that these 70 row IDs and four pair groups match the master assignment, and provide the current labelling protocol.
2. After Bryan reviews and submits his independent sheet, preserve that original version and compare by row ID with Bryce, Liando, ZD, and Yuhao's independent sheets. Do not use the AI-assisted draft as a human annotator's submission.
3. Return a disagreement list for Bryan-involved tickets. Resolve each with the paired annotator and record the adjudicated label separately.
4. Confirm the labelling protocol, disagreement log, agreement statistic, and frozen 175-ticket golden set before official model testing.

Status: AI-assisted first-pass draft complete; Bryan's own review, assignment confirmation, protocol reconciliation, pair comparison, adjudication, and golden-set freeze still pending.
