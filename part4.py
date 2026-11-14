"""Part 4: model-choice and architecture memo numbers. Run: python part4.py"""
import math

import numpy as np

from common import (confusion, knn_pos_share, part2_pipeline, predict_proba, rates,
                    write_csv, write_results)


def entropy(p, n):
    if n == 0:
        return 0.0
    e = 0.0
    for q in (p / n, 1 - p / n):
        if q > 0:
            e -= q * math.log2(q)
    return e


def gini(p, n):
    if n == 0:
        return 0.0
    q = p / n
    return 1.0 - q * q - (1 - q) ** 2


def main():
    S = part2_pipeline()
    X, y, tr, te = S["X"], S["y"], S["tr"], S["te"]
    Xtr_raw, Xte_raw = X[tr], X[te]
    ytr, yte = S["ytr"], S["yte"]
    out = []
    # 4.1
    n, P = len(ytr), int(np.sum(ytr))
    root_e, root_g = entropy(P, n), gini(P, n)
    conds = {"S1": lambda M: M[:, 5] == 1, "S2": lambda M: M[:, 6] == 1,
             "S3": lambda M: M[:, 2] > 0.5, "S4": lambda M: M[:, 0] <= 24}
    rows, ig, gg = [], {}, {}
    for name, f in conds.items():
        m = f(Xtr_raw)
        ny, py = int(np.sum(m)), int(np.sum(ytr[m]))
        nn, pn = n - ny, P - py
        ig[name] = root_e - (ny / n * entropy(py, ny) + nn / n * entropy(pn, nn))
        gg[name] = root_g - (ny / n * gini(py, ny) + nn / n * gini(pn, nn))
        rows.append([name, ny, py, nn, pn, ig[name], gg[name]])
    write_csv("part4_splits.csv", ["split", "n_yes", "positives_yes", "n_no", "positives_no",
                                   "info_gain", "gini_gain"], rows)
    best_ig = max(ig, key=lambda k: ig[k])  # first maximum in S1..S4 order
    best_gg = max(gg, key=lambda k: gg[k])
    out += [("root_entropy", root_e), ("root_gini", root_g),
            ("best_split_by_info_gain", best_ig), ("best_split_by_gini_gain", best_gg)]
    # 4.2
    m_tr = conds[best_ig](Xtr_raw)
    rate_yes = float(np.sum(ytr[m_tr])) / int(np.sum(m_tr))
    rate_no = float(np.sum(ytr[~m_tr])) / int(np.sum(~m_tr))
    out += [("stump_rate_yes", rate_yes), ("stump_rate_no", rate_no)]
    p_log = predict_proba(S["Xte"], S["w"], S["b"])
    k = S["best_k"]
    p_knn = knn_pos_share(S["Xtr"], ytr, S["Xte"], k)
    p_stump = np.where(conds[best_ig](Xte_raw), rate_yes, rate_no)
    pred_log, pred_stump = p_log >= 0.3, p_stump >= 0.3
    pred_knn = p_knn * k >= (k + 1) / 2
    hard = (pred_log.astype(int) + pred_knn.astype(int) + pred_stump.astype(int)) >= 2
    soft = (p_log + p_knn + p_stump) / 3 >= 0.3
    vrows = []
    for name, pred in (("logistic", pred_log), ("knn", pred_knn), ("stump", pred_stump),
                       ("hard_vote", hard), ("soft_vote", soft)):
        cells = confusion(yte, pred)
        r = rates(*cells)
        vrows.append([name, *cells, r["precision"], r["recall"], r["f1"]])
    write_csv("part4_voting.csv", ["model", "tp", "fp", "tn", "fn", "precision", "recall", "f1"], vrows)
    # 4.3
    yy = np.array([1, 1, 1, -1, -1, -1, 1, -1])
    h1 = np.array([1, 1, -1, -1, -1, -1, -1, -1])
    h2 = np.array([-1, 1, 1, -1, 1, -1, 1, -1])
    w = np.full(8, 1 / 8)
    arows, errs, alphas = [], [], []
    for rnd, h in ((1, h1), (2, h2)):
        eps = float(np.sum(w[h != yy]))
        alpha = 0.5 * math.log((1 - eps) / eps)
        un = w * np.exp(-alpha * yy * h)
        new = un / float(np.sum(un))
        for i in range(8):
            arows.append([rnd, i + 1, w[i], un[i], new[i]])
        errs.append(eps)
        alphas.append(alpha)
        w = new
    write_csv("part4_adaboost.csv", ["round", "point", "weight_before", "weight_unnormalised",
                                     "weight_after"], arows)
    score = alphas[0] * h1 + alphas[1] * h2
    ens_acc = float(np.sum(np.sign(score) == yy)) / 8  # a zero score counts as wrong
    out += [("round1_error", errs[0]), ("round1_alpha", alphas[0]),
            ("round2_error", errs[1]), ("round2_alpha", alphas[1]),
            ("ensemble_accuracy", ens_acc)]
    # 4.4
    out.append(("oob_fraction", (1 - 1 / 560) ** 560))
    # 4.5
    def conv(cin, cout, f):
        return f * f * cin * cout + cout

    def dense(a, b):
        return a * b + b

    def side(i, f, pad, stride):
        return (i - f + 2 * pad) // stride + 1

    s1 = side(28, 5, 2, 1)
    p1 = side(s1, 2, 0, 2)
    s2 = side(p1, 5, 0, 1)
    p2 = side(s2, 2, 0, 2)
    flat = p2 * p2 * 16
    layers = [("mlp_hidden1", dense(784, 16)), ("mlp_hidden2", dense(16, 16)),
              ("mlp_output", dense(16, 10)), ("cnn_conv1", conv(1, 6, 5)),
              ("cnn_conv2", conv(6, 16, 5)), ("cnn_dense1", dense(flat, 32)),
              ("cnn_dense2", dense(32, 10))]
    write_csv("part4_architecture.csv", ["layer", "parameters"], [list(r) for r in layers])
    d = dict(layers)
    out += [("mlp_total", d["mlp_hidden1"] + d["mlp_hidden2"] + d["mlp_output"]),
            ("cnn_total", d["cnn_conv1"] + d["cnn_conv2"] + d["cnn_dense1"] + d["cnn_dense2"]),
            ("fc_layer_params", dense(128 * 128 * 3, 1024)),
            ("conv_layer_params", conv(3, 64, 3)),
            ("rnn_total", 128 * 64 + 128 * 128 + 16 * 128 + 128 + 16)]
    write_results("part4_results.txt", out)
    print("cnn shapes: conv1 %d, pool1 %d, conv2 %d, pool2 %d, flat %d" % (s1, p1, s2, p2, flat))


if __name__ == "__main__":
    main()
