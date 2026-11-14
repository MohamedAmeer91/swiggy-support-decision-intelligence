"""Part 3: segmentation and dimensionality reduction. Run: python part3.py"""
import numpy as np

from common import load_records, mean, standardise_columns, write_csv, write_results

NAMES = ["E1", "E2", "E3", "E4", "E5", "E6"]
DISS = [
    [0.0, 7.9, 7.4, 2.9, 2.9, 6.1],
    [7.9, 0.0, 1.4, 5.9, 5.3, 2.0],
    [7.4, 1.4, 0.0, 5.8, 4.6, 1.3],
    [2.9, 5.9, 5.8, 0.0, 2.8, 4.5],
    [2.9, 5.3, 4.6, 2.8, 0.0, 3.4],
    [6.1, 2.0, 1.3, 4.5, 3.4, 0.0],
]


def kmeans(Z, k):
    """Pinned K-means. Returns (labels, centroids, wcss, passes)."""
    n = len(Z)
    step = n // k
    cent = Z[[i * step for i in range(k)]].copy()
    labels = None
    passes = 0
    while True:
        passes += 1
        d = np.stack([np.sum((Z - c) ** 2, axis=1) for c in cent], axis=1)
        new = np.argmin(d, axis=1)  # first minimum: ties go to the lower centroid
        if labels is not None and np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            members = Z[labels == j]
            if len(members):
                cent[j] = np.sum(members, axis=0) / len(members)
    wcss = float(sum(np.sum((Z[labels == j] - cent[j]) ** 2) for j in range(k)))
    return labels, cent, wcss, passes


def linkage_distance(a, b, how):
    ds = [DISS[i][j] for i in a for j in b]
    if how == "single":
        return min(ds)
    if how == "complete":
        return max(ds)
    return sum(ds) / len(ds)


def agglomerate(how):
    clusters = [(i,) for i in range(6)]
    merges = []
    while len(clusters) > 1:
        best = None
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = linkage_distance(clusters[i], clusters[j], how)
                if best is None or d < best[0]:
                    best = (d, i, j)
        d, i, j = best
        a, b = clusters[i], clusters[j]
        merges.append((a, b, d))
        clusters = [c for t, c in enumerate(clusters) if t not in (i, j)] + [tuple(sorted(a + b))]
    return merges


def label(c):
    return "+".join(NAMES[i] for i in sorted(c))


def clusters_at_cut(merges):
    h = [m[2] for m in merges]
    gaps = [h[i + 1] - h[i] for i in range(len(h) - 1)]
    g = gaps.index(max(gaps))
    return 6 - (g + 1)


def main():
    X, y, v = load_records()
    raw = X[:, :5]
    mu, sd, Z = standardise_columns(raw)
    out = []
    # 3.1
    wcss = {}
    for k in range(2, 7):
        lab, cent, wcss[k], passes = kmeans(Z, k)
        if k == 3:
            labels3 = lab
        print("K=%d passes=%d" % (k, passes))
    out += [("wcss_k%d" % k, wcss[k]) for k in range(2, 7)]
    # 3.2
    elbow = None
    for k in (3, 4, 5):
        if wcss[k] - wcss[k + 1] < 0.5 * (wcss[k - 1] - wcss[k]):
            elbow = k
            break
    if elbow is None:
        elbow = 5  # not reached on the reference data; documented in docs/DECISIONS.md
    out.append(("elbow_k", elbow))
    # 3.3
    means_x3 = [mean(raw[labels3 == j, 2]) for j in range(3)]
    order = sorted(range(3), key=lambda j: means_x3[j])
    seg_rows, seg_idx = [], {}
    for name, j in zip("ABC", order):
        idx = labels3 == j
        seg_idx[name] = idx
        seg_rows.append([name, int(np.sum(idx))] + [mean(raw[idx, c]) for c in range(5)]
                        + [mean(y[idx].astype(float)), mean(v[idx])])
    assert sum(r[1] for r in seg_rows) == len(y)
    write_csv("part3_segments.csv",
              ["segment", "size", "mean_X1", "mean_X2", "mean_X3", "mean_X4", "mean_X5",
               "outcome_rate", "mean_value"], seg_rows)
    out += [("size_segment_%s" % r[0], r[1]) for r in seg_rows]
    # 3.4
    hrows, cuts = [], {}
    for how in ("single", "complete", "average"):
        merges = agglomerate(how)
        for no, (a, b, d) in enumerate(merges, 1):
            a, b = sorted((a, b), key=lambda c: min(c))
            hrows.append([how, no, label(a), label(b), d])
        cuts[how] = clusters_at_cut(merges)
    write_csv("part3_hierarchical.csv", ["linkage", "merge_no", "cluster_a", "cluster_b", "height"], hrows)
    out += [("%s_clusters_at_cut" % how, cuts[how]) for how in ("single", "complete", "average")]
    # 3.5 PCA in seven steps
    mvec = np.array([mean(Z[:, j]) for j in range(5)])  # step 1 (zeros)
    C = Z - mvec                                        # step 2
    S = (C.T @ C) / (len(C) - 1)                        # step 3
    vals, vecs = np.linalg.eigh(S)                      # step 4
    o = np.argsort(-vals, kind="stable")                # step 5
    vals, vecs = vals[o], vecs[:, o]
    for j in range(5):
        if vecs[np.argmax(np.abs(vecs[:, j])), j] < 0:
            vecs[:, j] = -vecs[:, j]
    W = vecs[:, :2]                                     # step 6
    P = C @ W                                           # step 7
    total = float(np.sum(vals))
    out.append(("eigenvalue_sum", total))
    out += [("eigenvalue_%d" % (j + 1), vals[j]) for j in range(5)]
    out += [("explained_ratio_%d" % (j + 1), vals[j] / total) for j in range(5)]
    cum = np.cumsum(vals) / total
    out += [("cumulative_ratio_%d" % (j + 1), cum[j]) for j in range(5)]
    out.append(("components_for_80pct", int(np.argmax(cum >= 0.8)) + 1))
    for c in (0, 1):
        out += [("pc%d_loading_X%d" % (c + 1, j + 1), vecs[j, c]) for j in range(5)]
    for r in range(3):
        out += [("row%d_pc1" % (r + 1), P[r, 0]), ("row%d_pc2" % (r + 1), P[r, 1])]
    out += [("mean_pc1_segment_%s" % s, mean(P[seg_idx[s], 0])) for s in "ABC"]
    write_results("part3_results.txt", out)


if __name__ == "__main__":
    main()
