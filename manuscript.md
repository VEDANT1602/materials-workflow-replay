# Which analysis choices let a reader recover a materials result?

**Vedant Thaker**  
Working paper · 18 November 2026

## Abstract

Two analysts can have the same data and prompt yet disagree about the better model. We test which missing decisions explain that disagreement using 236 observations of copper thermal expansion from the NIST Hahn1 dataset. We fit a cubic and a continuous linear spline with four coefficients each. Across 24 combinations of temperature range, holdout rule, coordinate and evaluation weights, the spline has lower prediction error in 15 cases and the cubic in nine. We hide subsets of the four fields and enumerate the analyses consistent with each partial archive. Knowing the range, holdout and coordinate identifies the winning model in 22 of 24 specifications. None of those partial records determines both numerical scores. Adding the weights recovers both scores in all 24. The two ambiguous specifications use the same 40 test observations. Changing only their weights reverses the ranking. The benchmark separates recovery of a model choice from recovery of the evidence behind it.

## What does an archive promise a second analyst?

Two readers can start with the same public copper measurements and draw different conclusions. Given the instruction “compare the fits,” each must still decide which temperatures to hold back and how much weight to give their prediction errors. Exhaustively replaying the choices makes it possible to tell when the surviving record determines the answer and when one plausible guess happens to recover it.

Lei, Docherty and Cooper describe how language models can translate ambiguous materials-science requests into executable work [1]. For a reader revisiting that work, the convenience creates a bookkeeping problem. The input text may survive in full even when choices made during implementation have disappeared. Workflow Run RO-Crate provides a way to record the inputs, outputs and actions of an execution at several levels of detail [2]. A multiverse analysis makes plausible variations in analysis decisions visible [3]. Here, those ideas serve a narrower experiment. We treat the archive as partial information about a known set of programs and ask whether its omissions can change a model-selection decision. The contribution is a materials example with an enumerable answer, an example of a ranking reversal, and a small archive that someone else can replay offline.

## One copper dataset, two four-parameter fits

NIST's Hahn1 file contains paired temperature and expansion-coefficient observations from a copper study. The 236 rows span 14.13 to 851.61 K and include 235 distinct temperatures [4]. The archived data file comes from the Ceres Solver copy of the NIST benchmark [5]. An input check evaluates NIST's published seven-parameter rational curve on those rows and obtains a residual sum of squares of 1.53243828557, within 0.00000001 of the certified value. The rational curve verifies the response and predictor columns and numerical scale. The model comparison below serves as the test payload for an archive. It does not seek a replacement for NIST's reference curve.

The example prompt asks which of a cubic and a continuous piecewise-linear model predicts held-out temperatures more accurately. The cubic contains a constant, linear, quadratic and cubic term. The linear spline contains a constant, a slope and two positive-part hinge terms, with knots at the one-third and two-thirds empirical quantiles of the training coordinate. Both use ordinary least squares. Coordinate means, standard deviations and knots are fitted on training rows. The extrapolated spline follows its last fitted slope. Each test fold contains observations at temperatures absent from training, including when one recorded temperature occurs twice. The program checks that all design matrices have full column rank.

Four fields define the complete primary grid. The first admits either all observations or only measurements at 77 K and above, a deliberately specified lower cutoff. The second holds out either every fifth distinct temperature, the middle fifth of the sorted distinct temperatures, or the hottest fifth. The middle and tail boundaries use rounded-down rank indices as specified in the code. The third fits both models in absolute temperature or in the natural logarithm of absolute temperature. The fourth gives each observed row equal weight or gives the occupied bins of five equal-width test-temperature intervals equal total weight. The fit itself is unweighted in both cases. The response stays in the original file units throughout.

## How to score a partial archive

Each of the 24 complete specifications takes a turn as the original analysis. For each of the 16 subsets of recorded fields, the replay routine collects all complete specifications consistent with that partial description. A model decision is identified if every compatible specification chooses the same winner. A score pair is identified if both root-mean-square errors (RMSEs), rounded to eight decimal places, agree throughout the set. The replay is blind to which compatible specification was the original when deciding agreement. Each original specification counts once. These counts describe an explicitly enumerated design space. They do not estimate how frequently analysts would select any branch.

“Prompt alone” in this experiment already gives the rerunner considerable help. The data file, comparison code, list of possible field values and model classes are available. Only the field assignments are missing. In a real prompt-only archive, many more implementations could be consistent with the text. Conversely, a lab that uses fixed documented defaults might eliminate some of the alternatives by convention.

## Which fields recover the decision?

| Recorded fields | Compatible runs per archive | Winner identified / 24 | Score pair identified / 24 |
|---|---:|---:|---:|
| None | 24 | 0 | 0 |
| Temperature range and coordinate | 6 | 12 | 0 |
| Holdout and coordinate | 4 | 12 | 0 |
| Range, coordinate and weights | 3 | 15 | 0 |
| Range, holdout and coordinate | 2 | 22 | 0 |
| All four fields | 1 | 24 | 24 |

![Figure 1](figure.png)

Figure 1. A change in evaluation weights reverses the model ranking with identical predictions on the same 40 held-out observations. Lower RMSE is better. The specification uses interleaved temperatures at or above 77 K and fits both models in kelvin.

The spline has lower RMSE in 15 specifications and the cubic in nine. In the absence of a field assignment, neither decision follows uniquely. No single field guarantees a winner for any source specification. Knowing the range and coordinate identifies the decision in 12 cases, even though each partial description still permits six executions. Another two-field record, range and evaluation weights, resolves zero. Archive length measured in number of fields is a poor proxy for what a reader can recover.

The remaining disagreement after recording range, holdout and coordinate is instructive. Consider the 40 interleaved test observations at 77 K and above with both models fitted in kelvin. With equal weight per observation, the cubic has RMSE 0.433 and the spline 0.445. Giving each occupied temperature bin the same total weight changes those values to 0.404 and 0.362. The ranking reverses. No coefficient or prediction changed. The two records answer different questions about how prediction error should be distributed across the tested temperature range.

The largest errors illustrate a different omission. With the full temperature range and observation weighting, the cubic in kelvin has RMSE 23.928 on the hot tail, compared with 0.221 for the spline. On the interleaved test the values are 1.030 and 0.617. A large difference in extrapolation can coexist with a modest difference on interpolation. Recording “held-out error” alone would conceal the distinction. In a sensitivity analysis, adding two spline knots increases the spline to six coefficients and changes three of the 24 winning models. The field-identification counts in the table apply to the matched four-coefficient comparison.

## What would an independent rerun add?

The full manifest uniquely identifies a member of the enumerated grid by construction. The empirical findings are the amount of information lost by each omission and the actual size of the changes in error. A bitwise-identical file proves that two readers have the same input. It says nothing about how either reader divided the temperatures or averaged errors. A matching winner alone can also conceal substantial numerical disagreement.

The archived prompt is an illustrative specification written for this experiment. No language model was repeatedly sampled to generate the 24 branches. No independent human rerunner was timed or scored. This design assumes access to exactly the same code and enumerates four choices on a single measured response. A stronger usability test would give independent rerunners the prompt and input hash, randomize which archived fields they receive, and score both the conclusion and its numerical reconstruction before revealing the reference output. A second corpus outside materials science would show which of the fields transfer across domains. Those questions bear directly on the proposed design of usable generative-workflow archives [6].

## Data and code availability

The companion directory includes the original Hahn1 reference file, an executable Python script, an example machine-readable manifest, the primary results, the full archive-ablation table and the six-coefficient sensitivity results. Running `python run.py` regenerates these files with Python and NumPy. The reported run used NumPy 1.26.0. The manifest records the source-file hash. The compact test for a recovered conclusion is whether all compatible replays agree. Reporting whether their scores also agree makes the claim more precise.

## Research and writing assistance

Vedant Thaker supplied the research brief and source materials. OpenAI Codex assisted with study design, implementation, execution, literature review and drafting. Clever Humanizer suggested edits to the abstract. The final wording was checked against the analysis.

## References

[1] G. Lei, R. Docherty and S. J. Cooper. Materials science in the era of large language models: a perspective. Digital Discovery, 2024. https://doi.org/10.1039/D4DD00074A

[2] S. Leo et al. Recording provenance of workflow runs with RO-Crate. PLOS ONE, 2024. https://doi.org/10.1371/journal.pone.0309210

[3] S. Steegen, F. Tuerlinckx, A. Gelman and W. Vanpaemel. Increasing transparency through a multiverse analysis. Perspectives on Psychological Science, 2016. https://doi.org/10.1177/1745691616658637

[4] National Institute of Standards and Technology. Hahn1, thermal expansion of copper. Statistical Reference Datasets. https://itl.nist.gov/div898/strd/nls/data/LINKS/i-hahn1.shtml

[5] Ceres Solver. NIST Hahn1 test fixture, containing the observations and certified comparison. https://ceres-solver.googlesource.com/ceres-solver/+/master/data/nist/Hahn1.dat

[6] Imperial College London. Usable and reproducible genAI workflow archiving for open science. Design Engineering PhD Scholarship 7. https://www.imperial.ac.uk/design-engineering/study/phd/funding-opportunities/design-engineering-scholarships/design-engineering-phd-scholarships-deps/design-engineering-phd-scholarship-7/
