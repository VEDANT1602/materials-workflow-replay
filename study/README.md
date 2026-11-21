# Catalog-dependent AUC recovery

The current paper scores archived OpenML evaluations. It does not report a human or language-model experiment. The two catalogs contain only task IDs, dataset names, run and flow IDs, published performance metrics and, for later pages, their offset. Raw examples and OpenML account metadata are not distributed.

## Reproduce the paper from the archived values

Use Python 3.12. The two commands use only the standard library. Run from this directory in a working copy.

```sh
python catalog_dependence.py
python check_expansion.py
```

The first command recreates `catalog_expansion.csv`, `page_flow_counts.csv` and `mixed_page_draws.csv`. The second independently checks all 12 headline counts with sorted rational-valued signatures and ties-to-even integer rounding. Exact AUC differences are used throughout. Reports in the fixed first-page panel always have a matching source in each candidate set. All members, including singletons, enter the denominator. No run train/test predictions were regenerated for the catalog analysis.

- `catalog.csv` and `api_sources.csv` describe the first 384 evaluations per task.
- `page_catalog.csv`, `page_sources.csv` and `page_joins.csv` cover the disjoint offsets 384, 1,536 and 3,072. Each later task–metric request yielded 384 rows. All task–page intersections across the three metrics contained 384 run IDs. The first and later panels share no run IDs.
- `catalog_expansion.csv` separates report membership, candidate scope and reporting format. Counts can be summed over the seven tasks because the target samples have equal sizes within every column. A rate for one task uses that task's own report count.
- `mixed_page_draws.csv` gives all four coverage counts for each of 200 samples drawn from the observed pages. With Python's Random generator seeded from 21112026 through 21112225 inclusive, the program selects 384 distinct runs per task. Source ordering and task iteration are fixed by the CSVs and script. These are fixed-size composition checks. Their extrema are descriptive sample statistics.
- `aggregation_audit.csv`, `aggregate_predictions.py` and `prediction_sources.csv` document the separate reconstruction of two independent archived AUC summaries from prediction files. The multiclass score for run 73 uses a class-frequency weighted one-vs-rest AUC on pooled predictions; the binary score for run 28 uses both classes with equal AUC. The predictions are retrieved from OpenML separately.

## Refresh public sources

A fresh API query may return a different page as the public service changes. To preserve the archived tables, use another copy of this directory. `get_catalog.py` fetches the first page. `catalog_pages.py` fetches the three additional pages and prints the responses for the excluded task. Both download commands can write raw response caches outside the software directory. Public report URLs and SHA-256 digests identify the actual retrieved responses. The downloaded data are public OpenML metric values, and rights to upstream datasets and predictions remain with their providers.

```sh
python get_catalog.py --cache ../first-api-cache
python catalog_pages.py --cache ../later-api-cache
python catalog_dependence.py
python check_expansion.py
```

## Preparation and historical evidence

`references.md` identifies the sources and locations underlying the current manuscript. Previous responder experiments, protocols and diagnostics, including model outputs, are retained at [their published commit](https://github.com/VEDANT1602/materials-workflow-replay/tree/7f2f14f759fc8cc6cd31432f04b58a35dec60b9f/study). Neither the historical responder outputs nor any planned human blinding materials enter the paper's estimates.
