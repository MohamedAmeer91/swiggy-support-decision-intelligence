"""Part 2: classification and evaluation. Run: python part2.py"""
import math

import numpy as np

from common import (confusion, knn_predict, part2_pipeline, predict_proba, rates,
                    train_logistic, bce, write_csv, write_results)


def main():
    S = part2_pipeline()
    Xtr, Xte, ytr, yte = S["Xtr"], S["Xte"], S["ytr"], S["yte"]
    w, b, losses = S["w"], S["b"], S["losses"]
    out = []
    # 2.1
    out += [("train_rows", len(ytr)), ("train_positives", int(np.sum(ytr))),
            ("test_rows", len(yte)), ("test_positives", int(np.sum(yte)))]
    # 2.2
    p_te = predict_proba(Xte, w, b)
    p_tr = predict_proba(Xtr, w, b)
    out += [("loss_epoch_%d" % e, losses[e]) for e in (0, 1, 10, 100, 1000)]
    out += [("weight_X%d" % (j + 1), w[j]) for j in range(7)]
    out += [("bias", b), ("test_bce", bce(yte, p_te))]
    # 2.3
    for eta in (0.01, 0.1, 1.0):
        _, _, l = train_logistic(Xtr, ytr, eta, 200, record=(200,))
        out.append(("loss_epoch_200_eta_%s" % eta, l[200]))
    # 2.4
    out += [("odds_ratio_X%d" % (j + 1), math.exp(w[j])) for j in range(7)]
    # 2.5
    for tau in (0.5, 0.3):
        cells = confusion(yte, p_te >= tau)
        r = rates(*cells)
        for k, val in zip(("tp", "fp", "tn", "fn"), cells):
            out.append(("tau_%s_%s" % (tau, k), val))
        for k in ("accuracy", "precision", "recall", "f1", "specificity"):
            out.append(("tau_%s_%s" % (tau, k), r[k]))
    out.append(("blind_accuracy", float(np.sum(yte == 0)) / len(yte)))
    # 2.6
    rows = []
    for k in range(1, 10):
        tau = k / 10
        cells = confusion(yte, p_te >= tau)
        r = rates(*cells)
        rows.append([tau, *cells, r["recall"], r["fpr"]])
    write_csv("part2_thresholds.csv", ["tau", "tp", "fp", "tn", "fn", "tpr", "fpr"], rows)
    # 2.7
    write_csv("part2_knn_cv.csv", ["K", "mean_cv_f1"], [[k, f] for k, f in S["knn_table"]])
    best_k = S["best_k"]
    pred, _ = knn_predict(Xtr, ytr, Xte, best_k)
    cells = confusion(yte, pred)
    r = rates(*cells)
    out.append(("knn_best_k", best_k))
    for k, val in zip(("tp", "fp", "tn", "fn"), cells):
        out.append(("knn_" + k, val))
    out += [("knn_" + k, r[k]) for k in ("accuracy", "precision", "recall", "f1")]
    # 2.8
    def cost(y, pred):
        _, fp, _, fn = confusion(y, pred)
        return 50 * fp + 400 * fn
    best_tau, best_cost = None, None
    for k in range(1, 20):
        c = cost(ytr, p_tr >= k / 20)
        if best_cost is None or c < best_cost:
            best_tau, best_cost = k / 20, c
    out += [("cost_tau", best_tau), ("cost_train_at_tau", best_cost),
            ("cost_test_at_tau", cost(yte, p_te >= best_tau)),
            ("cost_test_at_0.5", cost(yte, p_te >= 0.5)),
            ("cost_test_flag_nobody", cost(yte, np.zeros(len(yte), dtype=bool)))]
    write_results("part2_results.txt", out)


if __name__ == "__main__":
    main()
