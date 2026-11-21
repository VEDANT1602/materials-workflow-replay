# Can rounded classifier scores identify an archived result?

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

21 November 2026

### Abstract

A reader has the dataset name and the accuracy printed in a benchmark table, but the run identifier and area under the ROC curve (AUC) are missing. How precisely can the reader recover the AUC? Across 2,688 public OpenML runs on seven classification tasks, accuracy rounded to a whole percentage point constrained AUC to within 0.01 for 1,066 runs (39.66%). Adding Cohen’s kappa rounded to one decimal place raised coverage to 1,110 (41.29%). Retaining an extra decimal place in both fields raised coverage to 2,216 (82.44%). In a blinded trial, two small instruction-tuned models each identified 56 of 112 source runs under either coarse report. A rule that checked the visible fields identified 59 when kappa was available. Even two runs with identical unrounded accuracy and kappa exhibited a 0.259483 AUC difference. A stable run identifier preserves information that additional digits recover unevenly across tasks.

## A missing run identifier

Accuracy and Cohen’s kappa summarize the predicted class labels. AUC also uses the order of the scores assigned to those labels [1]. A reader tracing a finding to its source therefore faces two questions. Does the printed row identify the archived run? If several runs fit, do their AUCs agree closely enough to recover the missing number? OpenML links runs to task and workflow identifiers and stores evaluation metrics [2, 3], so both questions can be checked against public experimental records.

A multiverse analysis enumerates reasonable choices in processing or analysis [4]. Here the candidate results already existed before the audit. An observed difference between compatible runs can be checked against the original records, even when several runs share a workflow. Work on computational reproduction with independent human analysts documents practical errors in recovering analysis decisions [5]. The experiment here isolates one earlier step, linking the numbers in a report to an archived run.

## Cases and recovery criterion

Eight specified OpenML classification task IDs were queried on 21 November 2026. Task 44 returned “Unknown task” and no evaluations. For each remaining task the first 384 entries returned for each of predictive accuracy, kappa and AUC were intersected by run ID. All 384 records per task survived the join and range checks. These pages cover 180 distinct flow IDs. A flow identifies a workflow implementation, and multiple parameter choices or runs can use the same flow. The query order and the fixed page limit confine inference to this catalog.

For one original run, collect every archived run on the same task whose displayed fields agree after decimal rounding, with ties rounded to even. For catalog grouping, positive and negative zero denote the same number. The source is identifiable when the set has one member. Let L and H be the lowest and highest archived AUC among the candidates. Their midpoint is within 0.01 of every candidate exactly when H − L ≤ 0.02. The reported coverage is the fraction of original runs satisfying that criterion. The 0.01 tolerance specifies the precision of the recovery question. It carries no claim about what AUC difference matters in an application. All comparisons weight the seven tasks equally.

## An extra digit helps more on some tasks

At whole-percentage accuracy, adding one decimal place of kappa moved 44 runs across the tolerance threshold. Coverage improved on three tasks and was unchanged on four. Its increase of 1.64 percentage points ranged from 0.95 to 1.91 points on omitting each task in turn. Exact source identification rose from 30 to 43 of 2,688 runs. The difference between identifying a run and identifying its missing metric is large on letter, where only 14 runs were unique under the coarse two-field export yet 324 had a tightly constrained AUC.

Reporting accuracy to 0.1 percentage point alone covered 1,721 runs (64.03%). Adding kappa to 0.01 then covered 2,216. The largest gains were on cmc, credit-g and diabetes. Precision cannot resolve all ranking differences. On credit-g, runs 256 and 578244 each had predictive accuracy 0.700000 and kappa 0.000000, yet their archived AUCs were 0.500000 and 0.759483. Both belong to the group of 27 runs with coarse report (70%, 0.0). This is the widest AUC range among the coarse two-field groups.

One widely reused flow, ID 2228, accounts for 1,204 runs (44.79%). In exploratory checks the coarse-kappa coverage gain was 3.02 percentage points after that flow was omitted and 3.50 points after retaining only the lowest-numbered run for each task–flow combination. Those rules change the comparison catalog. They show how candidate multiplicity affects the size of the gain.


| OpenML task | Accuracy 1 pp | + kappa 0.1 | Accuracy 0.1 pp | + kappa 0.01 |
| --- | --- | --- | --- | --- |
| kr-vs-kp | 65 | 65 | 132 | 132 |
| letter | 324 | 324 | 371 | 371 |
| mfeat-factors | 322 | 322 | 351 | 351 |
| cmc | 13 | 23 | 308 | 336 |
| optdigits | 312 | 312 | 372 | 372 |
| credit-g | 17 | 39 | 92 | 325 |
| diabetes | 13 | 25 | 95 | 329 |
| Total | 1,066 | 1,110 | 1,721 | 2,216 |
Table 1. Runs whose compatible AUC range spans at most 0.02. Each task contributes 384 runs. The kappa columns add the stated precision to the preceding accuracy column. pp = percentage points.

## Masked linkage against a field-matching rule

A locally frozen protocol sampled 16 disjoint pairs per task with identical whole-percentage accuracy. One member was selected at random under exact within-task left–right balance. Each pair generated two separate queries, first with the target’s accuracy and then with its accuracy and kappa. Both candidate cards always showed accuracy and kappa. Run IDs, task names, AUCs and the key were absent. The 224 query records per model contained 86 distinct rendered texts. Every distinct prompt started with empty model context.

Qwen2.5-0.5B-Instruct and SmolLM2-135M-Instruct are separately released model families [6, 7]. Local four-bit checkpoints were forced to choose A or B using the higher next-token logit. Both selected A in all 224 primary responses, matching a constant-position baseline. Each therefore got 56/112 in each condition, with mean absolute AUC error 0.00858. Kappa distinguished only four pairs. A leftmost-compatible rule got all four right, reached 59/112 overall with kappa, and reduced mean absolute error to 0.00650. Uniform guessing had 56/112 expected exact matches and expected absolute AUC error 0.00711 in both arms. The seven task-level accuracies of the rule with kappa give leave-one-task-out means of 51.04% to 53.13%.

To check whether the systems used an informative field at all, an exploratory positive control used 49 additional run pairs from four tasks. Both candidates matched accuracy, their rounded kappas differed, and each member served once as the target. The field-matching rule solved all 98 queries. Qwen solved 59 and selected A on 88. SmolLM2 solved 49 and selected A on all 98. These deliberately separable examples measure positional preference under this prompt. They provide no estimate of the prevalence of informative records or the accuracy of other prompts, checkpoints or people.

## Checking what the archived AUC means

As a check on the numerical reference, two public out-of-fold prediction files were read directly. For each class, AUC was computed from the ranks of the predicted scores, averaging tied ranks. For the chess task, run 28, pooling the predictions gave 0.97725267 against the archived 0.977253. Averaging the ten fold AUCs instead gave 0.97544136. For the digit task, run 73, pooling predictions and weighting one-versus-rest AUCs by class frequency gave 0.97008265 against the archived 0.970083. Equal class weights gave 0.97009003. These two checks recover published numbers to their six displayed decimals under the stated choices. They establish neither the scoring implementation used for every OpenML run nor successful refitting of a classifier.

## What to retain in a result table

Recording the run ID resolves the linkage problem directly while the archive remains accessible. When a numeric result must also stand on its own, the score name, precision, class weighting and treatment of folds matter. Workflow Run RO-Crate provides a machine-readable way to associate inputs, outputs and code with a run [8]. The source identifier and aggregation recipe serve different needs.

The catalog contains a fixed first page for each metric on seven tasks. Adding more runs can only preserve or enlarge an existing run’s compatible AUC range. The leave-one-task-out ranges describe sensitivity to these seven tasks and give no population confidence statement. The local protocol freeze has no external registration timestamp. Neither model was permitted to inspect the archive or write a reconstruction program. A human follow-up has prepared participant forms and a separately held scoring key. One task asks readers to identify records. A second asks them to write and return executable AUC calculations from eight anonymized prediction files unseen in the model study, with the aggregation instructions either supplied or withheld for all eight cases assigned to a reader. Blinded human linkage and re-execution have yet to be measured.

## Data and code availability

The supplement contains the OpenML run, flow and task IDs, 21 source requests with response hashes, scored records, exact prompts and model response logits. It also contains the aggregation audit, checkpoint download instructions, locally frozen protocol and blank forms for a future human study. The coordinator holds the unadministered case packets and answer keys separately. Sources for the two prediction files are listed in prediction_sources.csv. The inference software and scripts run locally.

[Study files, software and source records](https://github.com/VEDANT1602/materials-workflow-replay/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with the archive design, code, execution, literature checks and manuscript drafting. The same model family participated in preliminary reconstruction work, and one preliminary responder had prior exposure to a result. That pilot contributes no observations here. Qwen and SmolLM2 supplied the masked responses reported above. They received neither the manuscript nor the answer key.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] T. Fawcett. An introduction to ROC analysis. Pattern Recognition Letters 27, 861–874 (2006). <https://doi.org/10.1016/j.patrec.2005.10.010>

[2] J. Vanschoren, J. N. van Rijn and B. Bischl. Taking machine learning research online with OpenML. Proceedings of Machine Learning Research 41, 1–4 (2015). <https://proceedings.mlr.press/v41/vanschoren15.pdf>

[3] OpenML. Documentation for list_evaluations, the task-filtered run-evaluation interface. <https://openml.github.io/openml-python/main/generated/openml.evaluations.list_evaluations.html>

[4] S. Steegen, F. Tuerlinckx, A. Gelman and W. Vanpaemel. Increasing transparency through a multiverse analysis. Perspectives on Psychological Science 11, 702–712 (2016). <https://doi.org/10.1177/1745691616658637>

[5] N. Breznau et al. The reliability of replications: a study in computational reproductions. Royal Society Open Science 12, 241038 (2025). <https://doi.org/10.1098/rsos.241038>

[6] Qwen Team. Qwen2.5-0.5B-Instruct-GGUF. Version 9217f5d, Q4_K_M checkpoint. <https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/tree/9217f5db79a29953eb74d5343926648285ec7e67>

[7] Hugging Face Smol Models Research. SmolLM2-135M-Instruct. Model card and checkpoint documentation. <https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct>

[8] S. Leo et al. Recording provenance of workflow runs with RO-Crate. PLOS ONE 19, e0309210 (2024). <https://doi.org/10.1371/journal.pone.0309210>
