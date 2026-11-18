"""Check the headline results directly from the archived CSV files."""
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ("temperature_range", "holdout", "coordinate", "evaluation_weight")


def read_csv(name):
    with (ROOT / name).open(encoding="utf8", newline="") as stream:
        return list(csv.DictReader(stream))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf8"))
    data_sha = hashlib.sha256((ROOT / "Hahn1.dat").read_bytes()).hexdigest()
    expected_sha = "7e885af48e18a222033a66cb22b491f0f5bc761b652142c0d9b28132daf63956"
    check(data_sha == expected_sha == manifest["inputs"]["Hahn1.dat_sha256"], "NIST input checksum differs")
    primary = read_csv("results.csv")
    keys = [tuple(row[f] for f in FIELDS) for row in primary]
    check(len(set(keys)) == len(keys) == 24, "Expected 24 distinct comparison specifications")
    for row in primary:
        winner = min(("cubic", "spline"), key=lambda name: float(row[name+"_rmse"]))
        check(row["winner"] == winner, "Winner label disagrees with the recorded errors")
    check(Counter(row["winner"] for row in primary) == {"cubic": 9, "spline": 15}, "Unexpected model counts")

    archive = {row["fields"]:row for row in read_csv("archives.csv")}
    check(len(archive) == 16, "Expected 16 distinct archive conditions")
    for size in range(5):
        for retained in itertools.combinations(FIELDS, size):
            groups = defaultdict(list)
            for row in primary:
                groups[tuple(row[f] for f in retained)].append(row)
            known_winner = 0
            known_scores = 0
            for group in groups.values():
                if len({r["winner"] for r in group}) == 1:
                    known_winner += len(group)
                scores = {(round(float(r["cubic_rmse"]),8),round(float(r["spline_rmse"]),8)) for r in group}
                if len(scores) == 1:
                    known_scores += len(group)
            row = archive[" + ".join(retained) or "none"]
            check((known_winner,known_scores) == (int(row["conclusion_identified"]),int(row["score_pair_identified"])),
                  f"Archive count mismatch for {retained}")

    reversal = {row["evaluation_weight"]:row for row in primary if row["temperature_range"]=="at_least_77K"
                and row["holdout"]=="interleaved" and row["coordinate"]=="kelvin"}
    for weight, scores in {"observation":(.433,.445),"equal_bins":(.404,.362)}.items():
        row = reversal[weight]
        observed = tuple(round(float(row[col]),3) for col in ("cubic_rmse","spline_rmse"))
        check(observed == scores and int(row["n_test"])==40, "Held-out reversal differs")
    three_fields = archive["temperature_range + holdout + coordinate"]
    check((three_fields["conclusion_identified"],three_fields["score_pair_identified"])==("22","0"),
          "The key partial archive no longer reconstructs the published outcomes")
    print("Verified input, 24 model comparisons, 16 archive conditions and the 40-observation reversal.")


if __name__ == "__main__":
    main()
