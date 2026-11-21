def replay(x, y, case_id, fields):
    import numpy as np

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    options = {
        "range": ["all", "upper"],
        "holdout": ["interleaved", "middle", "hot"],
        "coordinate": ["raw", "log"],
        "weights": ["row", "bins"],
    }

    def score(c):
        keep = np.ones(x.size, dtype=bool) if c["range"] == "all" else x >= np.median(x)
        a, b = x[keep], y[keep]
        vals, ranks = np.unique(a, return_inverse=True)
        n = vals.size
        if c["holdout"] == "middle":
            test = (ranks >= int(.4*n)) & (ranks < int(.6*n))
        elif c["holdout"] == "hot":
            test = ranks >= int(.8*n)
        else:
            test = ranks % 5 == 2
        coordinate = np.log(a) if c["coordinate"] == "log" else a
        z = (coordinate - coordinate[~test].mean()) / coordinate[~test].std()
        knots = np.quantile(z[~test], [1/3, 2/3], method="linear")
        cubic = np.column_stack((np.ones_like(z), z, z**2, z**3))
        spline = np.column_stack((np.ones_like(z), z, np.maximum(0, z-knots[0]), np.maximum(0, z-knots[1])))
        weights = np.ones(test.sum())
        if c["weights"] == "bins":
            held = a[test]
            edges = np.linspace(held.min(), held.max(), 6)
            groups = np.searchsorted(edges[1:-1], held, side="right")
            weights = 1 / np.bincount(groups)[groups]
        scores = []
        for design in (cubic, spline):
            coef = np.linalg.lstsq(design[~test], b[~test], rcond=None)[0]
            err = b[test] - design[test] @ coef
            scores.append(float(np.sqrt(np.average(err**2, weights=weights))))
        return ("cubic" if scores[0] < scores[1] else "spline", *scores)

    candidates = [{}]
    for key, values in options.items():
        candidates = [{**c, key: value} for c in candidates for value in ([fields[key]] if key in fields else values)]
    outcomes = [score(c) for c in candidates]
    designation = "identified" if len({result[0] for result in outcomes}) == 1 else "uncertain"
    return (*outcomes[0], candidates[0], designation)
