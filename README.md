# How the candidate catalog changes the recovery of a missing classifier score

Reproducibility study by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana, USA.

Suppose a classification report names its task and gives rounded accuracy and Cohen’s kappa, but omits the run identifier and area under the ROC curve (AUC). Which reports still constrain the missing AUC to within 0.01? We held 2,688 public OpenML reports fixed and enlarged the set of candidate runs from 384 to 1,536 per task on seven tasks. For whole-percentage accuracy and one-decimal kappa, coverage fell from 1,110 reports (41.29%) to 792 (29.46%). At a finer precision it fell from 2,216 (82.44%) to 1,634 (60.79%). The extra 8,064 runs supplied previously missing counterexamples. A run identifier avoids the uncertainty caused by a changing candidate catalog. These counts describe the retrieved archive pages and do not measure a person’s ability to reconstruct an experiment.

[Paper (PDF)](manuscript.pdf) · [Editable text](manuscript.md) · [Methods and study files](study/README.md) · [Manuscript history](study/VERSION.md)

[Author-owned software license](LICENSE) · [Third-party terms](LICENSING.md) · [Previous version](https://github.com/VEDANT1602/materials-workflow-replay/tree/7f2f14f759fc8cc6cd31432f04b58a35dec60b9f)
