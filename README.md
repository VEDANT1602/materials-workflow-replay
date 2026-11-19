# The same 40 copper measurements select two different models

Two rows of the archived results use the same training set, held-out observations and model predictions. With one vote per observation, a cubic polynomial beats a two-knot linear spline on held-out error, 0.433 versus 0.445 RMSE. Giving each occupied temperature bin equal total weight reverses the result, 0.404 for the cubic versus 0.362 for the spline. The change is entirely in the scoring rule. [Both rows](results.csv?plain=1#L14)

![Held-out model ranking changes under two evaluation weights](figure.png)

The NIST Hahn1 copper thermal-expansion dataset contains 236 observations. Each model fits only the eligible rows in its training split. Repeated measurements at the same temperature stay together in the split. Each model fits four coefficients, with scaling and spline knots set from the training observations. The archive varies four choices: the eligible temperature range, holdout, coordinate transform, and weighting. [Training-only knots](run.py#L52) · [Original observations](Hahn1.dat)

## What could another analyst recover?

With the range, holdout and coordinate recorded, 22 of 24 specifications identify a winner, and none uniquely identifies both scores to eight decimal places. Adding the weighting field recovers both scores in all 24. An example prompt is included in the manifest as an experimental fixture. The replay enumerates a finite set of specifications. It measures ambiguity in this archive, regardless of how a future analyst might choose among the possibilities. [Archive comparisons](archives.csv) · [Manifest and recorded fields](manifest.json) · [Manuscript](manuscript.md) · [Paper PDF](manuscript.pdf)

## Reproduce the result

Use Python 3.11. The numerical run used NumPy 1.26.0. From the repository root:

```bash
python -m pip install -r requirements.txt
python run.py
python verify.py
```

The verifier uses the Python standard library. It also runs directly against the committed outputs. It checks the NIST input checksum, recomputes all 16 archive-field comparisons from the primary rows, and checks the 40-observation model reversal. To rebuild the figure, run:

```bash
python -m pip install -r requirements-plot.txt
python make_figure.py
```

## Input and archive

- [Hahn1.dat](Hahn1.dat) preserves the input observations, certified coefficients and residual. [NIST dataset description](https://itl.nist.gov/div898/strd/nls/data/LINKS/i-hahn1.shtml)
- [manifest.json](manifest.json) records the input and analysis checksums, runtime, example prompt and field dictionary.
- [archives.csv](archives.csv) covers all 16 choices of fields to retain. [six_parameter_spline.csv](six_parameter_spline.csv) repeats the comparison with two extra spline knots.

Maintained by Vedant Thaker.
