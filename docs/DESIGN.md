# DESIGN - Swiggy Support Decision Intelligence

Phase: DESIGN. Inputs: docs/REQUIREMENTS.md (the brief) and docs/PLAN.md.

## 1. Repository layout (tracked files)

```
README.md  requirements.txt  generate_data.py  .gitattributes  .gitignore
data/records.csv
common.py                       (shared helper; importing it runs nothing)
part1.py part2.py part3.py part4.py
outputs/part{1,2,3,4}_results.txt
outputs/part2_thresholds.csv part2_knn_cv.csv
outputs/part3_segments.csv part3_hierarchical.csv
outputs/part4_splits.csv part4_voting.csv part4_adaboost.csv part4_architecture.csv
docs/ (REQUIREMENTS, PLAN, DESIGN, DECISIONS)   tests/ (unittest)
```
The brief's layout lists required files and does not forbid extras ("shared helper files are fine");
docs/ and tests/ stay tracked (no images/PDFs/links). Decision recorded in DECISIONS.md.

## 2. Data and line endings

`generate_data.py` is committed verbatim. The csv module writes CRLF, and the MD5 is over those bytes,
so `.gitattributes` marks `data/records.csv` and `generate_data.py` as `-text` (no conversion on any OS).
Verify: `git cat-file -p HEAD:data/records.csv | md5sum` equals `7cb48ef89914049d76954530b6482e04`.
Other outputs are written with `\n` newlines by our code and are also `-text` for byte-stability.

## 3. common.py (no side effects on import)

- `load_records()` -> `(X: ndarray 800x7, y: int array, v: float array)` via csv module, skipping record_id.
- `fmt(v)`: bool -> yes/no, int -> `str`, float -> `%.4f` (negative zero normalised).
- `write_results(path, pairs)`: `key = value` lines; `write_csv(path, header, rows)`: exact header, `\n` newlines.
- `sample_sd(a)`, `ln` via numpy.
- `stratified_split(y)` -> `(train_idx, test_idx)` (floor(7*count/10) per class, file order).
- `standardise(train, other)` -> train mean, sample SD, standardised arrays.
- `sigmoid` (stable), `bce(y, p)` (clipped log), `train_logistic(X, y, eta, epochs, record=())` -> `(w, b, losses{epoch: loss})`.
- `confusion(y, pred)`, `rates(tp, fp, tn, fn)` -> accuracy, precision, recall, f1, specificity, fpr (0 on zero denominator).
- `knn_rank(ref, query)` stable-sorted neighbour order; `knn_prob(ref_X, ref_y, q, K)`; `select_knn_k(Xtr, ytr)` -> `(cv_table, best_K)`.
- `part2_pipeline()` -> dict with split, standardised matrices, logistic params, KNN K, so Part 4 reuses Part 2 by recomputation (deterministic), not by import-time execution.

## 4. Per-Part algorithms and outputs

Key order in every results file follows the task text order; ints as ints, floats 4 dp.

### Part 1 (all 800 rows)
1.1 n, mean_value, sd_value, se_value, ci95_low, ci95_high. 1.2 z_stat, reject_h0. 1.3 n_required = ceil((1.96 sd / 0.5)^2).
1.4 reg_slope, reg_intercept, tss, ess, rss, tss_equals_ess_plus_rss, r2, rmse, mae (hand-coded cov/var, divisor n-1).
1.5 gradient descent on z-scored X4, eta 0.1, 500 updates: gd_J0, gd_J1, gd_J10, gd_J100, gd_J500, gd_slope, gd_intercept, gd_slope_gap.
1.6 stable argsort of fitted values, halves of 400: resid_sd_lower_raw, resid_sd_upper_raw, resid_sd_ratio_raw, loglog_intercept, loglog_slope,
loglog_r2, loglog_rmse, resid_sd_lower_log, resid_sd_upper_log, resid_sd_ratio_log.
1.7 normal equation via numpy.linalg.solve: mr_beta_0..mr_beta_7, mr_r2, mr_adj_r2, loglog_adj_r2.

### Part 2
2.1 train_rows, train_positives, test_rows, test_positives. 2.2 loss_epoch_0/1/10/100/1000, weight_X1..X7, bias, test_bce.
2.3 loss_epoch_200_eta_0.01 / _0.1 / _1.0. 2.4 odds_ratio_X1..X7. 2.5 tau_0.5_{tp,fp,tn,fn,accuracy,precision,recall,f1,specificity},
same for tau_0.3_, blind_accuracy. 2.6 part2_thresholds.csv `tau,tp,fp,tn,fn,tpr,fpr` (tau 0.1..0.9, tau printed 4 dp; probabilities compared as p >= k/10).
2.7 part2_knn_cv.csv `K,mean_cv_f1` (11 rows); knn_best_k, knn_tp, knn_fp, knn_tn, knn_fn, knn_accuracy, knn_precision, knn_recall, knn_f1.
2.8 cost_tau, cost_train_at_tau, cost_test_at_tau, cost_test_at_0.5, cost_test_flag_nobody (cost = 50 fp + 400 fn; tau = k/20, k=1..19, first minimum).

### Part 3 (800 rows, X1..X5)
3.1 k-means (pinned start rows, argmin ties -> lower index, stop on first no-change pass, empty cluster keeps centroid), pass counts asserted in-code
as a self-check print only: wcss_k2..wcss_k6. 3.2 elbow_k. 3.3 size_segment_A/B/C, part3_segments.csv
`segment,size,mean_X1,mean_X2,mean_X3,mean_X4,mean_X5,outcome_rate,mean_value`.
3.4 hierarchical clustering from the 6x6 table, linkage by member-to-member distances, part3_hierarchical.csv
`linkage,merge_no,cluster_a,cluster_b,height`; single_clusters_at_cut, complete_clusters_at_cut, average_clusters_at_cut (largest gap, first on a tie).
3.5 PCA 7 steps with numpy.linalg.eigh, sign flip: eigenvalue_sum, eigenvalue_1..5, explained_ratio_1..5, cumulative_ratio_1..5, components_for_80pct,
pc1_loading_X1..5, pc2_loading_X1..5, row1_pc1, row1_pc2, row2_pc1, row2_pc2, row3_pc1, row3_pc2, mean_pc1_segment_A/B/C.
Key order in file: wcss, elbow_k, sizes, cut counts, PCA keys.

### Part 4
4.1 root_entropy, root_gini, part4_splits.csv `split,n_yes,positives_yes,n_no,positives_no,info_gain,gini_gain` (S1..S4), best_split_by_info_gain,
best_split_by_gini_gain (first on ties). 4.2 stump_rate_yes, stump_rate_no, part4_voting.csv `model,tp,fp,tn,fn,precision,recall,f1`
(logistic, knn, stump, hard_vote, soft_vote). 4.3 round1_error, round1_alpha, round2_error, round2_alpha, part4_adaboost.csv
`round,point,weight_before,weight_unnormalised,weight_after` (16 rows), ensemble_accuracy (sign 0 counts as wrong). 4.4 oob_fraction.
4.5 part4_architecture.csv `layer,parameters` (7 rows), mlp_total, cnn_total, fc_layer_params, conv_layer_params, rnn_total - all from shape formulas in code.

## 5. README outline (brief's order)
`Domain: Support` (line 1), `## How to run`, `## Part 1 findings` (R1.1-R1.5), `## Part 2 findings` (R2.1-R2.5), `## Part 3 findings` (R3.1-R3.4),
`## Part 4 findings` (R4.1-R4.4 incl. layer table), `## Model-choice memo` (<= 300 words), `## Limitations` (>= 3). Money as `INR n`. No URLs, no `$`.
All quoted numbers copied from outputs/.

## 6. Test strategy (tests/, stdlib unittest, run with `python -m unittest discover tests`)
- keys: every key named in the brief present, in order; formats (`key = value`, 4 dp floats, yes/no).
- CSV headers and row counts (9, 11, 3, 15, 4, 5, 16, 7); rate consistency with cell counts.
- checkpoints and invariants (800 rows, MD5 line, 560/119/240/51, tss=ess+rss, segment sizes sum 800, eigenvalue_sum 5, weights sum to 1).
- forbidden-content grep (polyfit, cov, corrcoef, lstsq, sklearn, pandas, scipy, `$`, http, image files).
- README order, first line, memo word count, quoted numbers appear in outputs.
- determinism: run each script twice into the repo, byte-compare outputs.

## 7. Deploy checklist
Clean clone in `_cleanclone_tmp`, fresh venv, `pip install -r requirements.txt`, README commands, diff outputs vs committed, delete clone,
clean working tree, only branch `main`, `git ls-files` review, no remotes, md5 via `git cat-file`.
