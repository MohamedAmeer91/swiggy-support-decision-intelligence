"""Part 1: estimation, inference and regression baseline. Run: python part1.py"""
import math

import numpy as np

from common import load_records, mean, sample_sd, write_results


def closed_form(x, y):
    mx, my = mean(x), mean(y)
    n = len(x)
    cov = float(np.sum((x - mx) * (y - my))) / (n - 1)
    var = float(np.sum((x - mx) ** 2)) / (n - 1)
    slope = cov / var
    return slope, my - slope * mx


def halves_sd(fitted, resid):
    order = np.argsort(fitted, kind="stable")
    lo, hi = resid[order[:400]], resid[order[400:]]
    return sample_sd(lo), sample_sd(hi)


def main():
    X, _, v = load_records()
    x4 = X[:, 3]
    n = len(v)
    out = []
    # 1.1
    m = mean(v)
    sd = sample_sd(v)
    se = sd / math.sqrt(n)
    out += [("n", n), ("mean_value", m), ("sd_value", sd), ("se_value", se),
            ("ci95_low", m - 1.96 * se), ("ci95_high", m + 1.96 * se)]
    # 1.2
    z = (m - 8.0) / se
    out += [("z_stat", z), ("reject_h0", abs(z) > 1.96)]
    # 1.3
    out += [("n_required", math.ceil((1.96 * sd / 0.5) ** 2))]
    # 1.4
    slope, icpt = closed_form(x4, v)
    fit = icpt + slope * x4
    tss = float(np.sum((v - m) ** 2))
    ess = float(np.sum((fit - m) ** 2))
    rss = float(np.sum((v - fit) ** 2))
    out += [("reg_slope", slope), ("reg_intercept", icpt), ("tss", tss), ("ess", ess),
            ("rss", rss), ("tss_equals_ess_plus_rss", abs(tss - ess - rss) < 1e-6 * tss),
            ("r2", 1 - rss / tss), ("rmse", math.sqrt(rss / n)),
            ("mae", float(np.sum(np.abs(v - fit))) / n)]
    # 1.5
    mx, sx = mean(x4), sample_sd(x4)
    zx = (x4 - mx) / sx
    mm, cc = 0.0, 0.0
    costs = {}
    for step in range(501):
        e = v - (mm * zx + cc)
        if step in (0, 1, 10, 100, 500):
            costs[step] = float(np.sum(e ** 2)) / n
        if step == 500:
            break
        gm = -2.0 / n * float(np.sum(zx * e))
        gc = -2.0 / n * float(np.sum(e))
        mm, cc = mm - 0.1 * gm, cc - 0.1 * gc
    gd_slope = mm / sx
    gd_icpt = cc - mm * mx / sx
    out += [("gd_J0", costs[0]), ("gd_J1", costs[1]), ("gd_J10", costs[10]),
            ("gd_J100", costs[100]), ("gd_J500", costs[500]), ("gd_slope", gd_slope),
            ("gd_intercept", gd_icpt), ("gd_slope_gap", abs(gd_slope - slope))]
    # 1.6
    lo, hi = halves_sd(fit, v - fit)
    lx, ly = np.log(x4), np.log(v)
    ls, li = closed_form(lx, ly)
    lfit = li + ls * lx
    lres = ly - lfit
    ltss = float(np.sum((ly - mean(ly)) ** 2))
    lrss = float(np.sum(lres ** 2))
    llo, lhi = halves_sd(lfit, lres)
    loglog_r2 = 1 - lrss / ltss
    out += [("resid_sd_lower_raw", lo), ("resid_sd_upper_raw", hi), ("resid_sd_ratio_raw", hi / lo),
            ("loglog_intercept", li), ("loglog_slope", ls), ("loglog_r2", loglog_r2),
            ("loglog_rmse", math.sqrt(lrss / n)), ("resid_sd_lower_log", llo),
            ("resid_sd_upper_log", lhi), ("resid_sd_ratio_log", lhi / llo)]
    # 1.7
    D = np.column_stack([np.ones(n), lx, X[:, 0], X[:, 1], X[:, 2], X[:, 4], X[:, 5], X[:, 6]])
    beta = np.linalg.solve(D.T @ D, D.T @ ly)
    rss_m = float(np.sum((ly - D @ beta) ** 2))
    r2 = 1 - rss_m / ltss
    adj = 1 - (1 - r2) * (n - 1) / (n - 7 - 1)
    out += [("mr_beta_%d" % i, beta[i]) for i in range(8)]
    out += [("mr_r2", r2), ("mr_adj_r2", adj),
            ("loglog_adj_r2", 1 - (1 - loglog_r2) * (n - 1) / (n - 1 - 1))]
    write_results("part1_results.txt", out)


if __name__ == "__main__":
    main()
