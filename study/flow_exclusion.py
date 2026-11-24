"""Compare nested catalog coverage with and without flow 2228 on both sides."""
import csv
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name):
    with (ROOT / name).open(newline="") as source:
        return list(csv.DictReader(source))


def covered_runs(rows, accuracy_step, kappa_step):
    """Return runs with a same-task, same-rounded-score AUC span at most .02."""
    groups = defaultdict(list)
    for row in rows:
        accuracy = Decimal(row["predictive_accuracy"]) * 100
        signature = (
            row["task"],
            accuracy.quantize(accuracy_step),
            Decimal(row["kappa"]).quantize(kappa_step),
        )
        groups[signature].append((row["run"], Decimal(row["area_under_roc_curve"])))

    covered = set()
    for members in groups.values():
        values = [auc for _, auc in members]
        if max(values) - min(values) <= Decimal("0.02"):
            covered.update(run for run, _ in members)
    return covered


def main():
    first = read("catalog.csv")
    later = read("page_catalog.csv")
    dominant = Counter(row["flow"] for row in first).most_common(1)[0][0]
    precision = (("coarse", Decimal("1"), Decimal("0.1")),
                 ("fine", Decimal("0.1"), Decimal("0.01")))
    fields = ("excluded_flow", "precision", "first_targets", "first_covered",
              "expanded_covered", "lost")
    with (ROOT / "flow_exclusion.csv").open("w", newline="") as result:
        writer = csv.DictWriter(result, fieldnames=fields)
        writer.writeheader()
        for omit in (None, dominant):
            targets = [row for row in first if row["flow"] != omit]
            candidates = targets + [row for row in later if row["flow"] != omit]
            target_ids = {row["run"] for row in targets}
            for label, accuracy_step, kappa_step in precision:
                before = covered_runs(targets, accuracy_step, kappa_step)
                after = covered_runs(candidates, accuracy_step, kappa_step) & target_ids
                assert after <= before
                writer.writerow(dict(excluded_flow=omit or "none", precision=label,
                                     first_targets=len(targets), first_covered=len(before),
                                     expanded_covered=len(after), lost=len(before - after)))


if __name__ == "__main__":
    main()
