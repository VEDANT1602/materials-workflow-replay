# Recoverability from incomplete analysis records | 21 November 2026

## Replay and check

Install NumPy 2.3.5 in Python 3.12, or use the revision lock in previous_revision/. Run these commands from this directory.

- `python recover.py` fits 72 primary cubic–spline comparisons and writes three_grids.csv and recovery.csv (3 datasets × 16 subsets × 4 tolerances = 192 rows).
- `python mask.py private-key` reproduces the 12 visible records and the original assignments. Keep the latter private during a new masked run. The supplied pilot has ended; the deterministic seed and key can now be inspected.
- `python score_blind.py` executes the two preserved responder functions on both held-back datasets. It checks retained fields and scores winners, exact RMSE pairs, pairs within 1% full-response SD, and ambiguity judgments. The complete blind_scored.csv gives all 24 responder-case observations.
- `python previous_revision/run.py` reruns the earlier independent copper reconstruction, phase sweep and knot sensitivity. Upstream Hahn1 code and outputs are pinned at [commit 4b7f708](https://github.com/VEDANT1602/materials-workflow-replay/tree/4b7f708f6d655c7636ed23efc23563da03b01604). The earlier eight-decimal accuracy check for the rational reference curve is documented there.

## Blind implementation procedure

PLAN.md was committed locally in `10e17febb2aa699c8808c09991003af3e4fedd87` at 2026-11-21 11:40:10 UTC before the external comparisons were scored. No public preregistration is claimed. The 12 cases use two external data assignments; prior copper results were known to the study designers. The exact prompt is masked_prompt.txt (SHA-256 `235e6a7d2850d0c8ad1e18e2dbc1593541606c45cf7c52921816511394543bb3`). Two separate assistant contexts received it. During no-tool reconstruction they received neither the source assignments nor trial outputs/data. One context had prior exposure to a copper headline in other project work. The same model family was used; exact model builds, sampling settings and token budgets were unavailable, so model inference itself cannot be exactly reproduced. Returned code is frozen and its execution can be reproduced. No feedback or scoring took place before the scripts were returned. Both used defaults consistent with the order in the prompt. This design measures these two implementations on the 12 assigned cases, without estimating human or cross-model averages.

## Inputs and rights

| File | Source, attribution and changes | SHA-256 |
|---|---|---|
| Hahn1.dat | Unmodified NIST/ITL copper thermal expansion benchmark, reference T. Hahn, NIST. The Ceres archive copy has the same digest. [NIST](https://www.itl.nist.gov/div898/strd/nls/data/hahn1.shtml) | 7e885af48e18a222033a66cb22b491f0f5bc761b652142c0d9b28132daf63956 |
| auto-mpg.data | R. Quinlan (1993), Auto MPG, UCI. Unchanged file from the official dataset archive. Code selects displacement and mpg only. [Dataset](https://doi.org/10.24432/C5859H) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 48b830e11feee5572525f8f1691ddb9d38d3d7b7063edcd8fca672c2a5e17d8d |
| abalone.data | W. Nash, T. Sellers, S. Talbot, A. Cawthorn and W. Ford (1994), Abalone, UCI. Unchanged file from the official archive. Code selects shell length and rings only; the source documents scaling of physical variables. [Dataset](https://doi.org/10.24432/C55C7W) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | de37cdcdcaaa50c309d514f248f7c2302a5f1f88c168905eba23fe2fbc78449f |

The data licenses are independent of software licensing. No rights in third-party code are newly granted.
