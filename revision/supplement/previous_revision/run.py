"""Reconstruct the Hahn1 analysis grid from the study specification and NIST data."""
from pathlib import Path
import csv
import hashlib
import itertools
import json
import platform

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Hahn1.dat"
EXPECTED_SHA256 = "7e885af48e18a222033a66cb22b491f0f5bc761b652142c0d9b28132daf63956"
FIELDS = ("range", "holdout", "coordinate", "weights")


def read_input():
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Unexpected Hahn1 input digest")
    y, x = np.loadtxt(DATA, skiprows=60, unpack=True)
    assert len(y) == 236 and len(np.unique(x)) == 235
    coefficients = [1.0776351733, -.12269296921, .0040863750610, -1.4262662514e-6,
                    -.0057609940901, .00024053735503, -1.2314450199e-7]
    numerator = np.polynomial.polynomial.polyval(x, coefficients[:4])
    denominator = np.polynomial.polynomial.polyval(x, [1, *coefficients[4:]])
    residual_sum = np.square(y - numerator / denominator).sum()
    assert abs(residual_sum - 1.5324382854) < 1e-8
    return x, y, digest, float(residual_sum)


def partitions(x, split, offset):
    unique = np.unique(x)
    n = len(unique)
    if split == "interleaved":
        held = unique[offset::5]
    elif split == "middle":
        held = unique[2*n//5:3*n//5]
    else:
        held = unique[4*n//5:]
    return np.isin(x, held)


def predictions(x, y, test, coordinate, knots):
    coordinate_values = np.log(x) if coordinate == "log" else x
    train_values = coordinate_values[~test]
    z = (coordinate_values - train_values.mean()) / train_values.std()
    positions = np.quantile(z[~test], np.arange(1, knots+1)/(knots+1))
    matrices = [np.column_stack([np.ones_like(z), z, z**2, z**3]),
                np.column_stack([np.ones_like(z), z, *(np.maximum(0, z-k) for k in positions)])]
    errors = []
    for matrix in matrices:
        beta, _, rank, _ = np.linalg.lstsq(matrix[~test], y[~test], rcond=None)
        assert rank == matrix.shape[1]
        errors.append(np.square(y[test] - matrix[test] @ beta))
    return errors


def run_grid(x_all, y_all, knots, offset=2):
    records = []
    for scope, split, coordinate in itertools.product(
        ("all", "ge77"), ("interleaved", "middle", "hottest"), ("kelvin", "log")
    ):
        included = x_all >= 77 if scope == "ge77" else np.ones_like(x_all, dtype=bool)
        x, y = x_all[included], y_all[included]
        test = partitions(x, split, offset)
        errors = predictions(x, y, test, coordinate, knots)
        bins = np.searchsorted(np.linspace(x[test].min(), x[test].max(), 6)[1:-1], x[test], side="right")
        for style in ("row", "bin"):
            w = np.ones(test.sum()) if style == "row" else 1/np.bincount(bins)[bins]
            cubic, spline = (float(np.sqrt(np.average(err, weights=w))) for err in errors)
            winner = "spline" if spline < cubic else ("cubic" if cubic < spline else "tie")
            records.append(dict(range=scope, holdout=split, coordinate=coordinate, weights=style,
                                n_test=int(test.sum()), cubic=cubic, spline=spline, winner=winner))
    return records


def ablate(records):
    rows = []
    for length in range(5):
        for fields in itertools.combinations(FIELDS, length):
            groups = {}
            for row in records:
                key = tuple(row[f] for f in fields)
                groups.setdefault(key, []).append(row)
            winner_count, score_count = 0, 0
            for group in groups.values():
                winner_count += len(group) * (len({r["winner"] for r in group}) == 1)
                scores = {(round(r["cubic"],8), round(r["spline"],8)) for r in group}
                score_count += len(group) * (len(scores) == 1)
            rows.append(dict(fields=",".join(fields) or "none", compatible=24//len(groups),
                             winner_recovered=winner_count, scores_recovered=score_count))
    return rows


def save(name, rows):
    with (ROOT / name).open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    x, y, digest, rss = read_input()
    grid = run_grid(x,y,2)
    sensitivity = run_grid(x,y,4)
    save("results.csv", grid)
    save("six-coefficient.csv", sensitivity)
    save("ablation.csv", ablate(grid))
    phases = []
    for offset in range(5):
        phase_grid = run_grid(x, y, 2, offset)
        partial = next(r for r in ablate(phase_grid) if r['fields'] == 'range,holdout,coordinate')
        phases.append(dict(offset=offset, spline_wins=sum(r['winner']=='spline' for r in phase_grid),
                           weight_omitted_winner_identified=partial['winner_recovered'],
                           interleaved_weight_reversals=sum(1 for i in range(0,len(phase_grid),2)
                               if phase_grid[i]['holdout']=='interleaved' and
                               phase_grid[i]['winner']!=phase_grid[i+1]['winner'])))
    save('interleaved_phase_sensitivity.csv', phases)
    manifest = dict(input="Hahn1.dat", input_sha256=digest, source="https://www.itl.nist.gov/div898/strd/nls/data/LINKS/DATA/Hahn1.dat",
                    reference_curve_rss=rss, python=platform.python_version(), numpy=np.__version__,
                    fields=list(FIELDS), score_rounding_decimals=8,
                    knot_quantiles="j/(k+1), j from 1 through k; NumPy linear method",
                    interleaved="sorted distinct temperatures, zero-based ranks 2, 7, ...",
                    middle="ranks floor(2n/5) through floor(3n/5)-1", hottest="ranks floor(4n/5) through n-1",
                    bin_weighting="five equal-width bins over the test range; each occupied bin has the same total weight")
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Spline wins:",sum(r["winner"]=="spline" for r in grid))
    print("Rankings changed at 4 knots:",sum(a["winner"]!=b["winner"] for a,b in zip(grid,sensitivity)))


if __name__ == "__main__":
    main()
