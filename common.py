"""Shared helpers for part1.py to part4.py. Importing this module runs nothing."""
import csv
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, "data", "records.csv")
OUT_DIR = os.path.join(ROOT, "outputs")


# ---------------------------------------------------------------- data and output
def load_records():
    """Return X (800x7 predictors X1..X7), y (outcome, int), v (value column)."""
    with open(DATA_PATH, newline="") as f:
        rows = list(csv.reader(f))[1:]
    X = np.array([[float(c) for c in r[1:8]] for r in rows])
    y = np.array([int(r[8]) for r in rows])
    v = np.array([float(r[9]) for r in rows])
    return X, y, v


def fmt(v):
    if isinstance(v, (bool, np.bool_)):
        return "yes" if v else "no"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, str):
        return v
    s = "%.4f" % float(v)
    return "0.0000" if s == "-0.0000" else s


def write_results(name, pairs):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", newline="\n") as f:
        for k, v in pairs:
            f.write("%s = %s\n" % (k, fmt(v)))


def write_csv(name, header, rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", newline="\n") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join(fmt(c) for c in r) + "\n")


# ---------------------------------------------------------------- statistics
def mean(a):
    return float(np.sum(a)) / len(a)


def sample_sd(a):
    m = mean(a)
    return math.sqrt(float(np.sum((a - m) ** 2)) / (len(a) - 1))


def standardise_columns(M):
    """Column mean and sample SD from M; return (mean, sd, standardised M)."""
    mu = np.array([mean(M[:, j]) for j in range(M.shape[1])])
    sd = np.array([sample_sd(M[:, j]) for j in range(M.shape[1])])
    return mu, sd, (M - mu) / sd


# ---------------------------------------------------------------- Part 2 machinery
def stratified_split(y):
    train, test = [], []
    for cls in (0, 1):
        idx = [i for i in range(len(y)) if y[i] == cls]
        k = (7 * len(idx)) // 10
        train += idx[:k]
        test += idx[k:]
    return np.array(sorted(train)), np.array(sorted(test))


def sigmoid(z):
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    e = np.exp(z[~pos])
    out[~pos] = e / (1.0 + e)
    return out


def bce(y, p):
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return float(-np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)) / len(y))


def train_logistic(X, y, eta, epochs, record=()):
    """Batch gradient descent from zero. Returns (w, b, {epoch: training loss})."""
    n = len(y)
    w = np.zeros(X.shape[1])
    b = 0.0
    losses = {}
    for ep in range(epochs + 1):
        p = sigmoid(X @ w + b)
        if ep in record:
            losses[ep] = bce(y, p)
        if ep == epochs:
            break
        err = p - y
        w = w - eta * (X.T @ err) / n
        b = b - eta * float(np.sum(err)) / n
    return w, b, losses


def predict_proba(X, w, b):
    return sigmoid(X @ w + b)


def confusion(y, pred):
    pred = np.asarray(pred).astype(bool)
    pos = np.asarray(y) == 1
    return (int(np.sum(pred & pos)), int(np.sum(pred & ~pos)),
            int(np.sum(~pred & ~pos)), int(np.sum(~pred & pos)))


def _div(a, b):
    return a / b if b else 0.0


def rates(tp, fp, tn, fn):
    acc = _div(tp + tn, tp + fp + tn + fn)
    prec = _div(tp, tp + fp)
    rec = _div(tp, tp + fn)
    f1 = _div(2 * prec * rec, prec + rec)
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1,
            "specificity": _div(tn, tn + fp), "fpr": _div(fp, fp + tn)}


def knn_pos_share(ref_X, ref_y, query_X, K):
    """Share of positive labels among the K nearest reference rows for each query row.
    Neighbours ranked by (distance, reference position) through a stable sort."""
    out = np.empty(len(query_X))
    for i, q in enumerate(query_X):
        d = np.sum((ref_X - q) ** 2, axis=1)
        order = np.argsort(d, kind="stable")[:K]
        out[i] = float(np.sum(ref_y[order])) / K
    return out


def knn_predict(ref_X, ref_y, query_X, K):
    share = knn_pos_share(ref_X, ref_y, query_X, K)
    return share * K >= (K + 1) / 2, share


def select_knn_k(Xtr, ytr):
    """5-fold CV (fold = position mod 5) on the standardised training rows."""
    folds = np.arange(len(ytr)) % 5
    ks = list(range(1, 22, 2))
    scores = {k: [] for k in ks}
    for f in range(5):
        ref, hold = folds != f, folds == f
        for k in ks:
            pred, _ = knn_predict(Xtr[ref], ytr[ref], Xtr[hold], k)
            scores[k].append(rates(*confusion(ytr[hold], pred))["f1"])
    table = [(k, sum(scores[k]) / 5.0) for k in ks]
    best = table[0]
    for row in table:
        if row[1] > best[1]:
            best = row
    return table, best[0]


def part2_pipeline():
    """Deterministic Part 2 state (split, standardised features, logistic model, KNN K)."""
    X, y, v = load_records()
    tr, te = stratified_split(y)
    mu, sd, Xtr = standardise_columns(X[tr])
    Xte = (X[te] - mu) / sd
    ytr, yte = y[tr], y[te]
    w, b, losses = train_logistic(Xtr, ytr, 0.1, 1000, record=(0, 1, 10, 100, 1000))
    table, best_k = select_knn_k(Xtr, ytr)
    return {"X": X, "y": y, "v": v, "tr": tr, "te": te, "Xtr": Xtr, "Xte": Xte,
            "ytr": ytr, "yte": yte, "w": w, "b": b, "losses": losses,
            "knn_table": table, "best_k": best_k}
