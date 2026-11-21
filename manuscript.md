# How the candidate catalog changes the recovery of a missing classifier score

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Reproducibility study

### Abstract

Suppose a classification report names its task and gives rounded accuracy and Cohen’s kappa, but omits the run identifier and area under the ROC curve (AUC). Which reports still constrain the missing AUC to within 0.01? We held 2,688 public OpenML reports fixed and enlarged the set of candidate runs from 384 to 1,536 per task on seven tasks. For whole-percentage accuracy and one-decimal kappa, coverage fell from 1,110 reports (41.29%) to 792 (29.46%). At a finer precision it fell from 2,216 (82.44%) to 1,634 (60.79%). The extra 8,064 runs supplied previously missing counterexamples. A run identifier avoids the uncertainty caused by a changing candidate catalog. These counts describe the retrieved archive pages and do not measure a person’s ability to reconstruct an experiment.

## The question a printed score can answer

Accuracy and kappa summarize classified labels. AUC also depends on how a classifier ranks examples [1]. OpenML assigns an identifier to each run and links that run to its task and workflow implementation, called a flow [2]. Suppressing the run identifier leaves a practical question: if several runs agree with a printed row, do their archived AUCs at least agree to the required precision?

For each report, group all same-task candidates that agree on the visible fields after decimal rounding, with ties rounded to even and signed zeros treated equally. Write L and H for the smallest and largest compatible AUC. A single estimate can lie within 0.01 of every candidate exactly when H − L ≤ 0.02. If the condition holds, the midpoint works. If it fails, the two endpoints themselves cannot both lie within 0.01 of any one estimate. The specified tolerance refers to the precision of reconstruction. A unique-run match is a separate event.

Adding candidate runs can only expand a group’s AUC range, provided the original reports remain fixed. This gives a direct test of apparent recovery: hold the reported rows and their rounding unchanged, add public runs that a reader could also have found, and count which guarantees disappear.

## Catalog and sampling order

The study covers seven OpenML classification tasks: kr-vs-kp (3), letter (6), mfeat-factors (12), cmc (23), optdigits (28), credit-g (31) and diabetes (37). A separate request for task 44 returned “Unknown task” and contributed no data. For each completed task, we downloaded accuracy, kappa and AUC evaluations, joined by run ID, and checked task, flow, finiteness and score ranges. OpenML’s evaluation interface supports task filters, page limits and offsets [3].

The first 384 records per metric and task gave 2,688 target reports. To test their dependence on the candidate set, we added three disjoint 384-entry pages per metric and task, at offsets 384, 1,536 and 3,072. All 384 runs joined across the three metrics on each page. The expanded catalog contained 10,752 distinct runs and 241 distinct flows. Candidates are always restricted to their report’s task. These fixed offsets provide extra competitors while preserving the target population. They are a convenience sample of archive pages. Runs at intervening and later offsets can further reduce fixed-report coverage.

The ordering clusters workflows. The four page positions across tasks contained 180, 57, 3 and 16 distinct flows respectively. Flow 2228 accounted for 1,204 of the 2,688 first-page runs (44.79%) and 1,764 of the 10,752 pooled runs (16.41%). Treating all runs as independent draws from a population of algorithms would give misleading precision.

## What changes when the reader searches further?

| Visible fields | First 2,688 reports, first-page candidates | Same reports, expanded candidates | All 10,752 reports, expanded candidates |
| --- | --- | --- | --- |
| Accuracy, 1 percentage point | 1,066 (39.66%) | 782 (29.09%) | 3,167 (29.45%) |
| Same accuracy + kappa to 0.1 | 1,110 (41.29%) | 792 (29.46%) | 3,192 (29.69%) |
| Accuracy, 0.1 percentage point | 1,721 (64.03%) | 1,207 (44.90%) | 4,925 (45.81%) |
| Same accuracy + kappa to 0.01 | 2,216 (82.44%) | 1,634 (60.79%) | 6,706 (62.37%) |

Table 1. Reports for which the full range of same-task compatible archived AUC values spans at most 0.02. The first two columns hold every reported run fixed. The last column also changes the target population. Each task has equal weight within a column.

With the coarse pair of fields, 318 original reports lost their guarantee. With the finer pair, 582 lost it. For the original targets, adding coarse kappa covered only 10 additional cases after expanding the search (792 versus 782). Even the fine report identified a unique run for only 162 of the original targets in the expanded catalog, although it constrained AUC for 1,634. On credit-g, for example, runs 256 and 578244 each have archived accuracy 0.700000 and kappa 0.000000, but their AUCs are 0.500000 and 0.759483. Printing those label metrics at their archived precision leaves the 0.259483 difference unresolved.

To isolate page composition at a fixed size, we also formed 200 catalogs by sampling 384 of the 1,536 retrieved runs uniformly without replacement within each task. In this sensitivity check each draw supplied its own target reports and candidates. Coarse two-field coverage ranged from 967 to 1,250 of 2,688 (35.97–46.50%). Fine two-field coverage ranged from 1,952 to 2,287 (72.62–85.08%). These ranges describe the specified draws from the observed pages. They do not estimate uncertainty over the entire archive.

## What to preserve in a benchmark table

The credit-g pair shows that AUC generally cannot be derived from accuracy and kappa alone. A compatible observed pair that disagrees is sufficient evidence of ambiguity. A catalog with no observed disagreement leaves open the possibility of other compatible runs. The difference is especially important when search results cluster by workflow.

A report can avoid a catalog search by recording the run ID with the metric and its aggregation convention. As a check on the archived target, we separately reconstructed two AUCs from public out-of-fold prediction files. Pooling predictions matched the six-decimal archived binary AUC for run 28 and the class-frequency-weighted multiclass AUC for run 73. Taking the mean of the per-fold AUCs produced different values in both cases. Those two checks do not establish how all archived AUCs were computed. The study addresses information preserved in an export; measuring analyst performance requires separately observed human reruns.

## Data and code availability

The supplement distributes the catalog of metric values, flow and run identifiers, source URLs and response hashes, join counts and precision calculations. It includes all per-task outputs and seeds for the fixed-size catalog draws. [Study code, source records and instructions](https://github.com/VEDANT1602/materials-workflow-replay/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with designing and running the archive comparisons, checking source material and drafting the manuscript. All results reported here come from archived classifier evaluations or computations on those evaluations.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] T. Fawcett. An introduction to ROC analysis. Pattern Recognition Letters 27, 861–874 (2006). <https://doi.org/10.1016/j.patrec.2005.10.010>

[2] J. Vanschoren, J. N. van Rijn and B. Bischl. Taking machine learning research online with OpenML. Proceedings of Machine Learning Research 41, 1–4 (2015). <https://proceedings.mlr.press/v41/vanschoren15.pdf>

[3] OpenML. Documentation for list_evaluations, the task-filtered run-evaluation interface. <https://openml.github.io/openml-python/main/generated/openml.evaluations.list_evaluations.html>
