# Can rounded classifier scores identify an archived result?

Working paper by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana. Correspondence: vedant.thaker1602@gmail.com.

A reader has the dataset name and the accuracy printed in a benchmark table, but the run identifier and area under the ROC curve (AUC) are missing. How precisely can the reader recover the AUC? Across 2,688 public OpenML runs on seven classification tasks, accuracy rounded to a whole percentage point constrained AUC to within 0.01 for 1,066 runs (39.66%). Adding Cohen’s kappa rounded to one decimal place raised coverage to 1,110 (41.29%). Retaining an extra decimal place in both fields raised coverage to 2,216 (82.44%). In a blinded trial, two small instruction-tuned models each identified 56 of 112 source runs under either coarse report. A rule that checked the visible fields identified 59 when kappa was available. Even two runs with identical unrounded accuracy and kappa exhibited a 0.259483 AUC difference. A stable run identifier preserves information that additional digits recover unevenly across tasks.

- [Read the paper](manuscript.pdf)
- [Read the plain-text manuscript](manuscript.md)
- [Reproduce the analysis and inspect the source and data records](study/README.md)
- [Software license](LICENSE) and [third-party terms](LICENSING.md)
- [Preparation record](study/PREPARATION.md)
- [Previous manuscript and supplements](https://github.com/VEDANT1602/materials-workflow-replay/tree/8c26d42b38d18174733b57c1ffd6b50c3fb8d4fa)
