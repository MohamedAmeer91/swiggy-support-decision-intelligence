"""Model state and calculations for the web layer. Read-only: nothing here writes files."""
import os
import sys
import threading

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import common  # noqa: E402  (importing common has no side effects)

FEATURES = ["customer_tenure_months", "earlier_ticket_count_90d", "sla_consumed_ratio",
            "account_value_inr_thousands", "satisfaction_score", "reopened_flag",
            "self_service_first_flag"]
COST_FP, COST_FN = 50.0, 400.0
KNN_KS = list(range(1, 42, 2))

_state = None
_lock = threading.RLock()
_knn_cache = {}


def _kmeans(Z, k):
    """Same pinned K-means as Part 3 (evenly spaced starting rows)."""
    step = len(Z) // k
    cent = Z[[i * step for i in range(k)]].copy()
    labels = None
    while True:
        d = np.stack([np.sum((Z - c) ** 2, axis=1) for c in cent], axis=1)
        new = np.argmin(d, axis=1)
        if labels is not None and np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            members = Z[labels == j]
            if len(members):
                cent[j] = np.sum(members, axis=0) / len(members)
    wcss = float(sum(np.sum((Z[labels == j] - cent[j]) ** 2) for j in range(k)))
    return labels, wcss


def _build():
    S = common.part2_pipeline()
    X, y, tr, te = S["X"], S["y"], S["tr"], S["te"]
    mu, sd, _ = common.standardise_columns(X[tr])
    p_tr = common.predict_proba(S["Xtr"], S["w"], S["b"])
    p_te = common.predict_proba(S["Xte"], S["w"], S["b"])
    # one-question tenure rule (Part 4 split S4: tenure <= 24), rates from training rows
    m_tr = X[tr][:, 0] <= 24
    rate_yes = float(np.sum(S["ytr"][m_tr])) / int(np.sum(m_tr))
    rate_no = float(np.sum(S["ytr"][~m_tr])) / int(np.sum(~m_tr))
    p_stump = np.where(X[te][:, 0] <= 24, rate_yes, rate_no)
    # segments and PCA on the five continuous predictors, all rows
    raw = X[:, :5]
    _, _, Z = common.standardise_columns(raw)
    wcss, labels3 = {}, None
    for k in range(2, 7):
        lab, wcss[k] = _kmeans(Z, k)
        if k == 3:
            labels3 = lab
    order = sorted(range(3), key=lambda j: common.mean(raw[labels3 == j, 2]))
    seg = np.empty(len(y), dtype=object)
    for name, j in zip("ABC", order):
        seg[labels3 == j] = name
    C = Z - Z.mean(axis=0)
    vals, vecs = np.linalg.eigh((C.T @ C) / (len(C) - 1))
    o = np.argsort(-vals, kind="stable")
    vals, vecs = vals[o], vecs[:, o]
    for j in range(5):
        if vecs[np.argmax(np.abs(vecs[:, j])), j] < 0:
            vecs[:, j] = -vecs[:, j]
    P = C @ vecs[:, :2]
    return {"S": S, "mu": mu, "sd": sd, "p_tr": p_tr, "p_te": p_te, "p_stump": p_stump,
            "wcss": wcss, "seg": seg, "pca": P, "eig": vals, "vecs": vecs}


def state():
    global _state
    if _state is None:
        with _lock:
            if _state is None:
                _state = _build()
    return _state


# ------------------------------------------------------------------ threshold lab
def _dataset(name):
    s = state()
    if name == "train":
        return s["p_tr"], s["S"]["ytr"]
    return s["p_te"], s["S"]["yte"]


def _cost(cells, cost_fp, cost_fn):
    tp, fp, tn, fn = cells
    return cost_fp * fp + cost_fn * fn


def confusion_dict(y, pred):
    cells = common.confusion(y, pred)
    r = common.rates(*cells)
    out = dict(zip(("tp", "fp", "tn", "fn"), cells))
    out.update(r)
    out["tpr"] = r["recall"]
    return out


def threshold(tau, dataset="test", cost_fp=COST_FP, cost_fn=COST_FN):
    p, y = _dataset(dataset)
    out = confusion_dict(y, p >= tau)
    cells = (out["tp"], out["fp"], out["tn"], out["fn"])
    out.update(dataset=dataset, tau=tau, cost_fp=cost_fp, cost_fn=cost_fn,
               cost=_cost(cells, cost_fp, cost_fn),
               cost_flag_nobody=cost_fn * int(np.sum(y)),
               cost_at_0_5=_cost(common.confusion(y, p >= 0.5), cost_fp, cost_fn),
               n=int(len(y)), positives=int(np.sum(y)))
    return out


def curve(dataset="test", cost_fp=COST_FP, cost_fn=COST_FN):
    p, y = _dataset(dataset)
    pts = []
    for i in range(101):
        tau = i / 100
        c = common.confusion(y, p >= tau)
        r = common.rates(*c)
        pts.append({"tau": tau, "tpr": r["recall"], "fpr": r["fpr"], "cost": _cost(c, cost_fp, cost_fn)})
    best = min(pts, key=lambda q: (q["cost"], q["tau"]))
    return {"dataset": dataset, "points": pts, "best_tau": best["tau"], "best_cost": best["cost"]}


# ------------------------------------------------------------------ KNN
def _knn_share(k):
    S = state()["S"]
    with _lock:
        if k not in _knn_cache:
            _knn_cache[k] = common.knn_pos_share(S["Xtr"], S["ytr"], S["Xte"], k)
        return _knn_cache[k]


def knn(k):
    S = state()["S"]
    share = _knn_share(k)
    out = confusion_dict(S["yte"], share * k >= (k + 1) / 2)
    cv = dict(S["knn_table"])
    out.update(k=k, best_k=S["best_k"], cv_f1=cv.get(k),
               cv=[{"k": a, "mean_cv_f1": b} for a, b in S["knn_table"]])
    return out


# ------------------------------------------------------------------ segments
def segments_extra():
    s = state()
    S = s["S"]
    pts = [{"pc1": round(float(s["pca"][i, 0]), 4), "pc2": round(float(s["pca"][i, 1]), 4),
            "segment": str(s["seg"][i]), "outcome": int(S["y"][i])} for i in range(len(S["y"]))]
    vals = s["eig"]
    return {"wcss": {str(k): v for k, v in s["wcss"].items()},
            "explained_ratio": [float(v / np.sum(vals)) for v in vals],
            "loadings": {"pc1": [float(v) for v in s["vecs"][:, 0]],
                         "pc2": [float(v) for v in s["vecs"][:, 1]],
                         "features": FEATURES[:5]},
            "points": pts,
            "segment_sizes": {n: int(np.sum(s["seg"] == n)) for n in "ABC"}}


# ------------------------------------------------------------------ model comparison
def compare(tau, cost_fp=COST_FP, cost_fn=COST_FN):
    s = state()
    S = s["S"]
    yte, k = S["yte"], S["best_k"]
    p_log, p_stump = s["p_te"], s["p_stump"]
    p_knn = _knn_share(k)
    pred_knn = p_knn * k >= (k + 1) / 2
    pred_log, pred_stump = p_log >= tau, p_stump >= tau
    hard = (pred_log.astype(int) + pred_knn.astype(int) + pred_stump.astype(int)) >= 2
    soft = (p_log + p_knn + p_stump) / 3 >= tau
    models = []
    for name, pred in (("logistic", pred_log), ("knn", pred_knn), ("stump", pred_stump),
                       ("hard_vote", hard), ("soft_vote", soft)):
        d = confusion_dict(yte, pred)
        d["model"] = name
        d["cost"] = _cost((d["tp"], d["fp"], d["tn"], d["fn"]), cost_fp, cost_fn)
        models.append(d)
    return {"tau": tau, "models": models}


# ------------------------------------------------------------------ score a record
def score(rec):
    s = state()
    S = s["S"]
    x = np.array([getattr(rec, f) for f in FEATURES], dtype=float)
    z = (x - s["mu"]) / s["sd"]
    p = float(common.predict_proba(z.reshape(1, -1), S["w"], S["b"])[0])
    contribs = [{"feature": f, "value": float(x[i]), "z": float(z[i]), "weight": float(S["w"][i]),
                 "effect": float(S["w"][i] * z[i])} for i, f in enumerate(FEATURES)]
    return {"probability": p, "flagged": p >= rec.tau, "tau": rec.tau, "bias": float(S["b"]),
            "contributions": contribs,
            "expected_cost_flag": rec.cost_fp * (1 - p),
            "expected_cost_skip": rec.cost_fn * p}


def meta():
    s = state()
    X = s["S"]["X"]
    feats = []
    for i, f in enumerate(FEATURES):
        feats.append({"name": f, "min": float(X[:, i].min()), "max": float(X[:, i].max()),
                      "mean": round(float(X[:, i].mean()), 4), "binary": f.endswith("_flag")})
    return {"features": feats, "cost_fp": COST_FP, "cost_fn": COST_FN,
            "best_k": s["S"]["best_k"], "knn_ks": KNN_KS,
            "rows": int(len(s["S"]["y"])), "train_rows": int(len(s["S"]["tr"])),
            "test_rows": int(len(s["S"]["te"]))}
