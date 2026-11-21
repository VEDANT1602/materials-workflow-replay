# Recovering a model decision from a partial Hahn1 archive

Run `python -m pip install -r requirements.txt`, then `python run.py`. The computation uses local data and needs no network after installation. Python 3.12.14 and NumPy 2.3.5 were used for this revision.

This independent implementation fits all 24 primary cases, repeats them for a four-knot spline, tests all 16 field subsets, and varies the interleaved split through all five possible rank offsets. It writes results.csv, six-coefficient.csv, ablation.csv, interleaved_phase_sensitivity.csv and manifest.json. Every fifth distinct temperature in the primary interleaved split starts with zero-based rank 2. All model comparisons use disjoint train/test temperatures.

Input: NIST/ITL Statistical Reference Datasets, Hahn1, 236 copper thermal-expansion observations. The input file is unmodified. Source: https://www.itl.nist.gov/div898/strd/nls/data/LINKS/DATA/Hahn1.dat . SHA-256: `7e885af48e18a222033a66cb22b491f0f5bc761b652142c0d9b28132daf63956`. The original repository used a Ceres Solver copy with identical bytes.

Original project: https://github.com/VEDANT1602/materials-workflow-replay/tree/4b7f708f6d655c7636ed23efc23563da03b01604 . To replay that implementation, clone and check out the named commit, then run `python run.py` and `python verify.py`. Both of those programs passed in the revision environment. The independent primary and four-knot RMSEs match the archived records within 1.1e-13. In the original script, the last two rational-curve constants differ slightly from the printed dataset reference. The independent script reads the printed values as specified; the checksum and all model comparisons are unaffected. The original reference-check residual was 1.532438285568, the corrected value is 1.532438285361, and the NIST-certified value is 1.5324382854.

License information: Hahn1.dat comes from the cited NIST benchmark. An open-source license for the original repository was not identified in this revision. New software licensing requires a decision by its rights holder. No license is granted here on another party’s behalf.

## Environment lock

Create separate Linux x86_64 virtual environments with CPython 3.12.14 for the revision and 3.11.9 for the baseline. In the activated revision environment run `python -m pip install --require-hashes -r revision-cp312-linux-x86_64.lock`. For the original checkout, install `baseline-cp311-linux-x86_64.lock` the same way in the baseline environment, then run the commands above. The baseline lock covers the public benchmark and its original figure. The revision lock covers the independent NumPy analysis. The lock headers identify the platform; the baseline transitive pins reconstruct a compatible environment for the published direct requirements.
