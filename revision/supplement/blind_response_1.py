def replay(x, y, case_id, fields):
    import numpy as np

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    options = {
        "range": ("all", "upper"),
        "holdout": ("interleaved", "middle", "hot"),
        "coordinate": ("raw", "log"),
        "weights": ("row", "bins"),
    }
    branches = {key: (fields[key],) if key in fields else values
                for key, values in options.items()}
    selected = {key: values[0] for key, values in branches.items()}

    def evaluate(scope, split, coordinate, weights):
        keep = x >= np.median(x) if scope == "upper" else np.ones(x.shape, dtype=bool)
        xr, yr = x[keep], y[keep]
        distinct, rank = np.unique(xr, return_inverse=True)
        n = len(distinct)
        if split == "interleaved":
            test = rank % 5 == 2
        elif split == "middle":
            test = (rank >= int(np.floor(0.4 * n))) & (rank < int(np.floor(0.6 * n)))
        else:
            test = rank >= int(np.floor(0.8 * n))
        values = np.log(xr) if coordinate == "log" else xr
        z = (values - values[~test].mean()) / values[~test].std(ddof=0)
        one = np.ones_like(z)
        k1, k2 = np.quantile(z[~test], [1.0 / 3, 2.0 / 3], method="linear")
        cubic = np.column_stack((one, z, z**2, z**3))
        spline = np.column_stack((one, z, np.maximum(z - k1, 0), np.maximum(z - k2, 0)))
        xtest = xr[test]
        if weights == "bins":
            edges = np.linspace(xtest.min(), xtest.max(), 6)
            bins = np.searchsorted(edges[1:-1], xtest, side="right")
            weight = 1.0 / np.bincount(bins, minlength=5)[bins]
        else:
            weight = np.ones_like(xtest)
        errors = []
        for design in (cubic, spline):
            coef = np.linalg.lstsq(design[~test], yr[~test], rcond=None)[0]
            residual = design[test] @ coef - yr[test]
            errors.append(float(np.sqrt(np.average(residual**2, weights=weight))))
        return ("cubic" if errors[0] < errors[1] else "spline", errors[0], errors[1])

    winners = set()
    chosen_scores = None
    for scope in branches["range"]:
        for holdout in branches["holdout"]:
            for coordinate in branches["coordinate"]:
                for weights in branches["weights"]:
                    choices = dict(range=scope, holdout=holdout, coordinate=coordinate, weights=weights)
                    result = evaluate(scope, holdout, coordinate, weights)
                    winners.add(result[0])
                    if choices == selected:
                        chosen_scores = result
    return (*chosen_scores, selected, "identified" if len(winners) == 1 else "uncertain")
