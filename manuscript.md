# How the candidate catalog changes the recovery of a missing classifier score

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Reproducibility study · November 24, 2026

### Abstract

A printed accuracy and Cohen’s kappa can match several archived classifier runs with different areas under the ROC curve (AUC). For a fixed report, adding candidates can only widen the compatible AUC range. The empirical question is how many reports lose a useful numerical bound. Across seven OpenML tasks, expanding the search from 384 to 1,536 candidates per task removed the ±0.01 guarantee for 318 of 1,110 initially covered reports at coarse rounding (28.65%) and 582 of 2,216 at finer rounding (26.26%). The 2,688 target reports stayed fixed. Four named classifiers were refitted on the published credit-g folds. Two had identical accuracy (0.700) and kappa (0), yet their six-decimal AUCs were 0.500000 and 0.759483. The catalog counts measure ambiguity within four retrieved pages per task. The refits show how that ambiguity arose for one pair of workflows.

## A bound for a report with a missing AUC

Accuracy and kappa summarize classified labels. AUC also depends on how a classifier ranks examples [1]. OpenML assigns an identifier to each run and links that run to its task and workflow implementation, called a flow [2]. Suppressing the run identifier leaves a practical question: if several runs agree with a printed row, do their archived AUCs at least agree to the required precision?

For each report, group all same-task candidates that agree on the visible fields after decimal rounding, with ties rounded to even and signed zeros treated equally. Write L and H for the smallest and largest compatible AUC. A single estimate can lie within 0.01 of every candidate exactly when H − L ≤ 0.02. If the condition holds, the midpoint works. If it fails, the two endpoints themselves cannot both lie within 0.01 of any one estimate. The specified tolerance refers to the precision of reconstruction. A unique-run match is a separate event.

Adding candidate runs can only expand a group’s AUC range, provided the original reports remain fixed. This gives a direct test of apparent recovery: hold the reported rows and their rounding unchanged, add public runs that a reader could also have found, and count which guarantees disappear.

## Catalog and sampling order

The study covers seven OpenML classification tasks: kr-vs-kp (3), letter (6), mfeat-factors (12), cmc (23), optdigits (28), credit-g (31) and diabetes (37). Retrieval records for excluded requests accompany the study files. For each completed task, we downloaded accuracy, kappa and AUC evaluations, joined by run ID, and checked task, flow, finiteness and score ranges. OpenML’s evaluation interface supports task filters, page limits and offsets [3].

The first 384 records per metric and task gave 2,688 target reports. To test their dependence on the candidate set, we added three disjoint 384-entry pages per metric and task, at offsets 384, 1,536 and 3,072. All 384 runs joined across the three metrics on each page. The expanded catalog contained 10,752 distinct runs and 241 distinct flows. Candidates are always restricted to their report’s task. These fixed offsets provide extra competitors while preserving the target population. They are a convenience sample of archive pages. Runs at intervening and later offsets can further reduce fixed-report coverage.

The ordering clusters workflows. The four page positions across tasks contained 180, 57, 3 and 16 distinct flows respectively. Flow 2228 accounted for 1,204 of the 2,688 first-page runs (44.79%) and 1,764 of the 10,752 pooled runs (16.41%). Treating all runs as independent draws from a population of algorithms would give misleading precision.

## Coverage as the candidate set grows

| Visible fields | First 2,688 reports, first-page candidates | Same reports, expanded candidates | All 10,752 reports, expanded candidates |
| --- | --- | --- | --- |
| Accuracy, 1 percentage point | 1,066 (39.66%) | 782 (29.09%) | 3,167 (29.45%) |
| Same accuracy + kappa to 0.1 | 1,110 (41.29%) | 792 (29.46%) | 3,192 (29.69%) |
| Accuracy, 0.1 percentage point | 1,721 (64.03%) | 1,207 (44.90%) | 4,925 (45.81%) |
| Same accuracy + kappa to 0.01 | 2,216 (82.44%) | 1,634 (60.79%) | 6,706 (62.37%) |

Table 1. Reports for which the full range of same-task compatible archived AUC values spans at most 0.02. The first two columns hold every reported run fixed. The last column also changes the target population. Each task has equal weight within a column.

The direction of the change follows from nesting the candidate sets. Its magnitude depends on which new runs were found. Of the 1,110 reports initially covered by the coarse pair, 318 (28.65%) lost coverage. Of the 2,216 covered by the finer pair, 582 (26.26%) lost coverage. For the original targets, adding coarse kappa covered only 10 additional cases after expanding the search (792 versus 782). Even the fine report identified a unique run for only 162 of the original targets in the expanded catalog, although it constrained AUC for 1,634. On credit-g, for example, runs 256 and 578244 each have archived accuracy 0.700000 and kappa 0.000000, but their AUCs are 0.500000 and 0.759483. Printing those label metrics at their archived precision leaves the 0.259483 difference unresolved.

A post hoc check removed the most frequent flow, 2228, from both targets and candidates. Among the 1,484 remaining targets, expanding the catalog reduced coarse two-field coverage from 638 to 320, a loss of 318. Fine two-field coverage fell from 1,201 to 967, a loss of 234. The original fine loss of 582 therefore depends strongly on catalog composition. Removing a flow changes both who is evaluated and which competing scores remain, so these differences cannot be attributed to the flow alone.

To isolate page composition at a fixed size, we also formed 200 catalogs by sampling 384 of the 1,536 retrieved runs uniformly without replacement within each task. In this sensitivity check each draw supplied its own target reports and candidates. Coarse two-field coverage ranged from 967 to 1,250 of 2,688 (35.97–46.50%). Fine two-field coverage ranged from 1,952 to 2,287 (72.62–85.08%). These ranges describe the specified draws from the observed pages. They do not estimate uncertainty over the entire archive.

## Retraining the two runs behind the credit-g example

We refitted ZeroR (run 256) and locally weighted decision stumps (run 578244) because they give the printed-score collision above. Two additional flows on the same task, OneR and a pruning tree (REPTree), checked the procedure on models that predict both classes. For each run we used its published class and options, the Weka release identified by its flow, and the ten train/test partitions from OpenML task 31 [4]. Each of the forty fits used 900 training rows, in the supplied order, and predicted 100 held-out rows with the outcome masked. Each run had one out-of-fold prediction per original example. The archived predictions entered the comparison only after fitting.

| Run | Workflow | Refit accuracy | Refit kappa | Refit AUC, full precision | Refit AUC, six-decimal probabilities | Archived AUC |
| --- | --- | --- | --- | --- | --- | --- |
| 256 | ZeroR | 0.700 | 0.000 | 0.500000 | 0.500000 | 0.500000 |
| 578244 | Locally weighted decision stump | 0.700 | 0.000 | 0.759486 | 0.759483 | 0.759483 |
| 51 | OneR | 0.663 | 0.067 | 0.528810 | 0.528810 | 0.528810 |
| 71 | REPTree | 0.701 | 0.230 | 0.714648 | 0.714648 | 0.714648 |
Table 2. Pooled out-of-fold binary AUC gives tied positive–negative pairs half credit. The two refit AUC columns differ only in the precision of the probabilities being ranked.

All 4,000 test labels agreed with their archived predictions. Every refit probability for the “good” class was within half a unit of the archive’s sixth decimal place. Both collision runs classified every row as “good.” ZeroR produced the same class probability for every row, whereas local weighting assigned different probabilities within the same predicted class. The second model therefore recovered a ranking that its reported accuracy and kappa could not reveal. Rounding its probabilities to the exported precision changed a few ties and reproduced the archived AUC to six decimal places.

## Records needed to reproduce a score

Preserving a run ID identifies which workflow to refit. Reproducing the last digits of a pooled AUC can also require the original folds, prediction precision and aggregation convention. A separate check on stored predictions for binary run 28 and multiclass run 73 reproduced the six-decimal AUC by pooling observations; averaging fold AUCs gave different values. The multiclass check used class-frequency-weighted one-vs-rest AUC. Those two checks and the four refits cover named runs. The four refits use one dataset and overlapping test examples, and the workflow choices were retrospective. No blinded participant reconstructed a run from a masked report, so these results cannot estimate analyst success.

## Data and code availability

The supplement distributes the catalog of metric values, flow and run identifiers, source URLs and response hashes, join counts and precision calculations. It includes the seeds and outputs for the fixed-size catalog draws and the source hashes, Weka settings, fitting code and aggregate prediction checks for the four model reruns. [Study code, source records and instructions](https://github.com/VEDANT1602/materials-workflow-replay/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with the catalog comparisons, classifier refits, source checks and drafting.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] T. Fawcett. An introduction to ROC analysis. Pattern Recognition Letters 27, 861–874 (2006). <https://doi.org/10.1016/j.patrec.2005.10.010>

[2] J. Vanschoren, J. N. van Rijn and B. Bischl. Taking machine learning research online with OpenML. Proceedings of Machine Learning Research 41, 1–4 (2015). <https://proceedings.mlr.press/v41/vanschoren15.pdf>

[3] OpenML. Documentation for list_evaluations, the task-filtered run-evaluation interface. <https://openml.github.io/openml-python/main/generated/openml.evaluations.list_evaluations.html>

[4] OpenML. German Credit classification task 31, official ten-fold partitions and run metadata. [Task and folds](https://www.openml.org/t/31) · [ZeroR run 256](https://www.openml.org/r/256) · [Locally weighted run 578244](https://www.openml.org/r/578244).
