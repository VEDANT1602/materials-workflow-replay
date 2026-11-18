"""Replay a finite set of analysis specifications on the NIST Hahn1 observations."""
import csv
import hashlib
import itertools
import json
import platform
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
FIELDS = {
    "temperature_range": ("all", "at_least_77K"),
    "holdout": ("interleaved", "interior_gap", "hot_tail"),
    "coordinate": ("kelvin", "log_kelvin"),
    "evaluation_weight": ("observation", "equal_bins"),
}


def read_data():
    source = HERE / "Hahn1.dat"
    raw = source.read_bytes()
    arr = np.loadtxt(source, skiprows=60)
    assert arr.shape == (236, 2)
    y, x = arr.T
    b = [1.0776351733, -.12269296921, .0040863750610, -.0000014262662514,
         -.0057609940901, .00024053738027, -.00000012314455327]
    numerator = np.polynomial.polynomial.polyval(x, b[:4])
    denominator = np.polynomial.polynomial.polyval(x, [1] + b[4:])
    certified_sse = np.sum((y - numerator / denominator) ** 2)
    assert np.isclose(certified_sse, 1.5324382854, atol=1e-8, rtol=0)
    return x, y, hashlib.sha256(raw).hexdigest(), certified_sse


def evaluate(x, y, spec, knot_count=2):
    keep = x >= (0 if spec["temperature_range"] == "all" else 77)
    x, y = x[keep], y[keep]
    unique_x, ranks = np.unique(x, return_inverse=True)
    n = len(unique_x)
    rule = spec["holdout"]
    if rule == "interleaved":
        test = (ranks % 5 == 2)
    elif rule == "interior_gap":
        test = (ranks >= int(.4*n)) & (ranks < int(.6*n))
    else:
        test = ranks >= int(.8*n)
    train = ~test
    assert not np.intersect1d(x[train], x[test]).size
    transformed = x if spec["coordinate"] == "kelvin" else np.log(x)
    z = (transformed - np.mean(transformed[train])) / np.std(transformed[train])
    knots = np.quantile(z[train], np.arange(1, knot_count+1)/(knot_count+1))
    cubic = np.column_stack([np.ones(len(z)), z, z*z, z**3])
    spline = np.column_stack([np.ones(len(z)), z, *(np.maximum(0, z-k) for k in knots)])
    residuals = []
    for basis in (cubic, spline):
        coef, _, rank, _ = np.linalg.lstsq(basis[train], y[train], rcond=None)
        assert rank == basis.shape[1]
        residuals.append(y[test] - basis[test] @ coef)
    bins = np.clip(((x[test]-x[test].min()) / np.ptp(x[test]) * 5).astype(int),0,4)
    weights = np.ones(test.sum()) if spec["evaluation_weight"] == "observation" else 1/np.bincount(bins)[bins]
    scores = [float(np.sqrt(np.average(res**2, weights=weights))) for res in residuals]
    return dict(**spec, n_train=int(train.sum()), n_test=int(test.sum()),
                cubic_rmse=scores[0], spline_rmse=scores[1],
                winner="cubic" if scores[0] < scores[1] else "spline")


def write_rows(path, records):
    with path.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def archives(records):
    """For every subset of fields, test whether all compatible worlds agree."""
    counts = []
    fields = tuple(FIELDS)
    for length in range(len(fields)+1):
        for subset in itertools.combinations(fields, length):
            groups = {}
            for r in records:
                signature = tuple(r[f] for f in subset)
                groups.setdefault(signature, []).append(r)
            identified, exact, compat = 0, 0, []
            for group in groups.values():
                size = len(group)
                winners = {r["winner"] for r in group}
                unique_scores = {(round(r["cubic_rmse"], 8), round(r["spline_rmse"], 8)) for r in group}
                identified += size * (len(winners) == 1)
                exact += size * (len(unique_scores) == 1)
                compat.append(size)
            counts.append(dict(fields=" + ".join(subset) or "none", recorded=length,
                               conclusion_identified=identified, score_pair_identified=exact,
                               specifications=len(records), compatible_per_archive=max(compat)))
    return counts


def main():
    x, y, sha, checked = read_data()
    specs = [dict(zip(FIELDS, items)) for items in itertools.product(*FIELDS.values())]
    primary = [evaluate(x, y, spec) for spec in specs]
    sensitivity = [evaluate(x, y, spec, knot_count=4) for spec in specs]
    write_rows(HERE / "results.csv", primary)
    write_rows(HERE / "archives.csv", archives(primary))
    write_rows(HERE / "six_parameter_spline.csv", sensitivity)
    archive = {
        "prompt": "Compare a cubic and a continuous piecewise-linear fit to the copper expansion measurements. Which predicts held-out temperatures more accurately?",
        "inputs": {"Hahn1.dat_sha256": sha, "observations": len(y), "certified_sse_crosscheck": checked},
        "retrieval": "https://raw.githubusercontent.com/ceres-solver/ceres-solver/master/data/nist/Hahn1.dat",
        "analysis": "run.py", "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": platform.python_version(), "python_packages": {"numpy": np.__version__},
        "field_dictionary": FIELDS, "selected_run_example": specs[0],
        "reproduce": "python run.py",
    }
    (HERE / "manifest.json").write_text(json.dumps(archive, indent=2)+"\n", encoding="utf-8")
    assert archives(primary)[-1]["score_pair_identified"] == len(primary)
    print(archive["inputs"])
    print("Primary winners", [sum(r["winner"] == c for r in primary) for c in ("cubic","spline")])
    print("Winner changes with extra spline knots", sum(a["winner"]!=b["winner"] for a,b in zip(primary,sensitivity)))


if __name__ == "__main__":
    main()
