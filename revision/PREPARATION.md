# Preparation record

Recovering model choices and scores from incomplete analysis records on three measured datasets

Vedant Thaker · 21 November 2026

## Original work

Vedant Thaker is the sole author. He designed the original workflow replay study, wrote its manuscript, developed its original software, and requested the comparisons and checks reported in this revision.

The author reports that the research project began on 2 August 2026. The previous versions and the new revision represent different stages of the work.

## Revision activities

OpenAI Codex assisted with the independent Hahn1 reconstruction, formalization and implementation of recovery metrics, additional public-dataset analyses, and masked generation, execution and scoring of two replay programs, as well as literature checks and preparation of the revised text. The author set the research question and requested the revision.

## Computational checks

A separate implementation reproduced the original 24 primary and 24 four-knot Hahn1 fits within 1.1 × 10⁻¹³ RMSE. All 72 primary designs across the three datasets passed finite-data, positive-coordinate and full-rank checks. Two returned functions were scored against the preassigned records without outcome-based edits. This comparison verifies their behavior on these inputs only.

## Data and version records

The original Hahn1 code and archived runs are available in the baseline repository. The revision supplement bundles three verified inputs, all 72 branch-level comparisons, 192 dataset/subset/tolerance records, the exact masked prompt, both unmodified responder functions, hidden-assignment generator and scored trial. Run python recover.py and python score_blind.py. Earlier four-knot and phase checks are in previous_revision/.

[Original pinned software](https://github.com/VEDANT1602/materials-workflow-replay/tree/4b7f708f6d655c7636ed23efc23563da03b01604) · [Revision code and data](https://github.com/VEDANT1602/materials-workflow-replay/tree/main/revision/supplement)

The reported checks are computational. No independent personal rerun or line-by-line review of these revisions by the author is asserted here.
