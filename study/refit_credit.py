"""Refit four archived credit-g workflows and compare row-aligned predictions."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import subprocess
import urllib.request
from itertools import groupby
from pathlib import Path

HERE = Path(__file__).resolve().parent


def acquire(cache):
    """Fetch input artifacts once and verify before using Weka or scoring."""
    cache.mkdir(parents=True, exist_ok=True)
    with (HERE / "refit_inputs.csv").open(newline="") as f:
        for spec in csv.DictReader(f):
            path = cache / spec["file"]
            if not path.exists():
                req = urllib.request.Request(spec["url"], headers={"User-Agent": "credit-g-refit/1"})
                with urllib.request.urlopen(req, timeout=120) as response:
                    raw = response.read()
                if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
                    raise ValueError(f"Source replaced or incomplete: {spec['url']}")
                path.write_bytes(raw)
            if hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
                raise ValueError(f"Input digest mismatch: {path}")


def refit(settings, cache):
    jars = [cache / f"weka-dev-{settings['version']}.jar",
            cache / f"pentaho-package-manager-{settings['manager_version']}.jar"]
    output = cache / f"fit-{settings['run']}.csv"
    # Fully qualified class resolution avoids Weka's obsolete Java 8 classpath scan.
    subprocess.run(["java", "-Dweka.test.maventest=true", "-Xmx512m", "--class-path",
                    os.pathsep.join(map(str, jars)), str(HERE / "RefitCredit.java"),
                    str(cache / "data-31.arff"), str(cache / "split-31.arff"), str(output),
                    *settings["options"]], check=True)
    with output.open(newline="") as f:
        return list(csv.DictReader(f))


def archived_rows(path):
    header, body = path.read_text().split("@data", 1)
    columns = [line.split()[1] for line in header.splitlines() if line.startswith("@attribute ")]
    rows = list(csv.DictReader(io.StringIO(body.strip()), fieldnames=columns))
    indexed = {(r["fold"], r["row_id"]): r for r in rows}
    assert len(indexed) == len(rows) == 1000 and {r["repeat"] for r in rows} == {"0"}
    return indexed


def auc(scores, truth):
    # Each positive-negative pair earns 1 for strict ordering, 1/2 for a tie.
    positives = sum(truth)
    negatives = len(truth) - positives
    twice_wins = seen_neg = 0
    for _, group in groupby(sorted(zip(scores, truth)), key=lambda pair: pair[0]):
        ys = [y for _, y in group]
        pos = sum(ys)
        neg = len(ys) - pos
        twice_wins += pos * (2 * seen_neg + neg)
        seen_neg += neg
    return twice_wins / (2 * positives * negatives)


def compare(settings, results, archived, catalog):
    n = len(results)
    pairs = [(r, archived[(r["fold"], r["row_id"])]) for r in results]
    assert n == 1000 and len({int(r["row_id"]) for r in results}) == n
    assert all(r["truth"] == a["correct"] and r["positive_class"] == "good" for r, a in pairs)
    truth = [r["truth"] == "good" for r in results]
    predicted = [r["predicted"] == "good" for r in results]
    accuracy = sum(x == y for x, y in zip(truth, predicted)) / n
    t, p = sum(truth), sum(predicted)
    chance = (t * p + (n - t) * (n - p)) / (n * n)
    kappa = (accuracy - chance) / (1 - chance)
    scores = [float(r["probability"]) for r in results]
    exported = [float(a["confidence.good"]) for _, a in pairs]
    assert all(math.isfinite(s) and 0 <= s <= 1 for s in scores + exported)
    errors = [abs(a-b) for a, b in zip(scores, exported)]
    return dict(run=settings["run"], flow=settings["flow"], workflow=settings["workflow"],
                task=31, folds=10, test_rows=n,
                matching_labels=sum(r["predicted"] == a["prediction"] for r, a in pairs),
                confidence_within_half_unit_at_6dp=sum(e <= 0.000000500001 for e in errors),
                max_confidence_difference=max(errors), fit_accuracy=accuracy, fit_kappa=kappa,
                fit_auc_full_precision=auc(scores, truth),
                fit_auc_probability_6dp=auc([round(s, 6) for s in scores], truth),
                auc_from_archived_predictions=auc(exported, truth),
                archived_accuracy=catalog["predictive_accuracy"], archived_kappa=catalog["kappa"],
                archived_auc=catalog["area_under_roc_curve"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path,
                        help="External directory for upstream files and row-level refit outputs")
    parser.add_argument("--output", type=Path, default=HERE / "refit_results.csv")
    args = parser.parse_args()
    cache = args.cache.resolve()
    acquire(cache)
    settings = json.loads((HERE / "refit_settings.json").read_text())
    with (HERE / "catalog.csv").open(newline="") as f:
        catalog = {int(r["run"]): r for r in csv.DictReader(f)}
    summaries = []
    for config in settings:
        run = config["run"]
        assert int(catalog[run]["task"]) == 31 and int(catalog[run]["flow"]) == config["flow"]
        # The learner sees only the original dataset and official split assignment.
        results = refit(config, cache)
        reference = archived_rows(cache / f"pred-{run}.arff")
        summaries.append(compare(config, results, reference, catalog[run]))
    with args.output.open("w", newline="") as dest:
        w = csv.DictWriter(dest, fieldnames=list(summaries[0]))
        w.writeheader()
        w.writerows(summaries)


if __name__ == "__main__":
    main()
