# How the candidate catalog changes the recovery of a missing classifier score

Reproducibility study by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana, USA. Revised November 24, 2026.

A printed accuracy and Cohen’s kappa can match several archived classifier runs with different areas under the ROC curve (AUC). For a fixed report, adding candidates can only widen the compatible AUC range. The empirical question is how many reports lose a useful numerical bound. Across seven OpenML tasks, expanding the search from 384 to 1,536 candidates per task removed the ±0.01 guarantee for 318 of 1,110 initially covered reports at coarse rounding (28.65%) and 582 of 2,216 at finer rounding (26.26%). The 2,688 target reports stayed fixed. Four named classifiers were refitted on the published credit-g folds. Two had identical accuracy (0.700) and kappa (0), yet their six-decimal AUCs were 0.500000 and 0.759483. The catalog counts measure ambiguity within four retrieved pages per task. The refits show how that ambiguity arose for one pair of workflows.

[Paper (PDF)](manuscript.pdf) · [Editable text](manuscript.md) · [Methods and study files](study/README.md) · [Manuscript history](study/VERSION.md)

[Author-owned software license](LICENSE) · [Third-party terms](LICENSING.md) · [Previous version](https://github.com/VEDANT1602/materials-workflow-replay/tree/dd25dfa4c070c7bd34a78c382b4a009138cb2d92)
