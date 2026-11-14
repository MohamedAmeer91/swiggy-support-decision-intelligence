# PLAN - Swiggy Support Decision Intelligence (Capstone, 100 marks)

Scope of this document: PLAN phase only. No design decisions beyond stack choice, no code.

## 1. Summary of the brief

One public GitHub repo, one branch (`main`), textual deliverables only. Synthetic data (800 rows, 10 columns) from a provided `generate_data.py`, committed verbatim. Four chained Parts, plain Python 3.10+ and NumPy, all graded quantities computed by our own code. Graders read committed `outputs/` files and the README; they do not run code, but code must regenerate the outputs exactly.

- Part 1 (25): CI and z-test on `resolution_minutes` (H0 mu = 8.0), sample-size calc, closed-form regression on X4, gradient-descent equivalent, funnel check and log-log remedy, normal-equation multiple regression.
- Part 2 (30): stratified 70/30 split (560/240), logistic regression from scratch, learning-rate comparison, odds ratios, threshold metrics, ROC sweep, KNN with 5-fold CV, INR cost-based threshold.
- Part 3 (25): K-means from scratch (pinned init), elbow, segment profile, hierarchical clustering (single/complete/average) on a given 6x6 table, PCA in seven steps.
- Part 4 (20): entropy/Gini splits, stump + hard/soft vote, two-round AdaBoost by hand, OOB fraction, NN parameter counting (MLP, CNN, RNN), memo.

## 2. Deliverables and marks mapped to tasks

The brief gives per-Part marks only (25/30/25/20); per-item weights are not published. Each results key, CSV and README answer is scored independently, so every key is a work item.

| Part (marks) | Task | Artifact / keys | README item |
|---|---|---|---|
| Setup | T0.1 | `generate_data.py` verbatim, `data/records.csv`, must print `800 10 170 7cb48ef89914049d76954530b6482e04` | - |
| Setup | T0.2 | `requirements.txt` (`numpy==<ver>`), repo layout, helper module | `## How to run` |
| P1 (25) | 1.1 | n, mean_value (chk 8.9382), sd_value, se_value, ci95_low/high | R1.1 |
| P1 | 1.2 | z_stat, reject_h0 | R1.1 (Type I, practical size) |
| P1 | 1.3 | n_required (+/-1 earns half) | R1.2 |
| P1 | 1.4 | reg_slope, reg_intercept, tss, ess, rss, tss_equals_ess_plus_rss, r2, rmse, mae | - |
| P1 | 1.5 | gd_J0/J1/J10/J100/J500, gd_slope, gd_intercept, gd_slope_gap (<0.001) | R1.3 |
| P1 | 1.6 | resid_sd_{lower,upper}_raw, ratio_raw, loglog_{intercept,slope,r2,rmse}, resid_sd_*_log, ratio_log (stable sort) | R1.4 |
| P1 | 1.7 | mr_beta_0..7, mr_r2, mr_adj_r2, loglog_adj_r2 | R1.5 |
| P2 (30) | 2.1 | train_rows/positives, test_rows/positives (560/119/240/51) | - |
| P2 | 2.2 | loss_epoch_0/1/10/100/1000, weight_X1..X7, bias, test_bce | - |
| P2 | 2.3 | loss_epoch_200_eta_{0.01,0.1,1.0} | R2.1 |
| P2 | 2.4 | odds_ratio_X1..X7 | R2.2 |
| P2 | 2.5 | tau_0.5_* and tau_0.3_* (9 keys each), blind_accuracy | R2.3 |
| P2 | 2.6 | `part2_thresholds.csv` (9 rows) | - |
| P2 | 2.7 | `part2_knn_cv.csv` (11 rows), knn_best_k, knn_tp..knn_f1 | R2.4 |
| P2 | 2.8 | cost_tau (exact), cost_train_at_tau, cost_test_at_tau, cost_test_at_0.5, cost_test_flag_nobody | R2.5 |
| P3 (25) | 3.1 | wcss_k2..k6 (chk wcss_k2 = 2262.6753) | R3.1 |
| P3 | 3.2 | elbow_k | R3.1 |
| P3 | 3.3 | size_segment_A/B/C, `part3_segments.csv` (3 rows) | R3.2 |
| P3 | 3.4 | `part3_hierarchical.csv` (15 rows), single/complete/average_clusters_at_cut | R3.3 |
| P3 | 3.5 | eigenvalue_sum (chk 5.0000), eigenvalue_1..5, explained/cumulative_ratio_1..5, components_for_80pct, pc1/pc2_loading_X1..X5, row1..3_pc1/pc2, mean_pc1_segment_A/B/C | R3.4 |
| P4 (20) | 4.1 | root_entropy (chk 0.7462), root_gini, `part4_splits.csv` (4 rows), best_split_by_info_gain/gini_gain | R4.1 |
| P4 | 4.2 | stump_rate_yes/no, `part4_voting.csv` (5 rows) | R4.2 |
| P4 | 4.3 | round1/2_error, round1/2_alpha, `part4_adaboost.csv` (16 rows), ensemble_accuracy (chk round1_error 0.2500) | R4.3 |
| P4 | 4.4 | oob_fraction | - |
| P4 | 4.5 | `part4_architecture.csv` (7 rows), mlp_total, cnn_total, fc_layer_params, conv_layer_params, rnn_total | R4.4 (layer table, shapes, activations, vanishing gradient) |
| P4 | 4.6 | memo <= 300 words, >= 3 numbers from outputs, threshold + INR cost, logistic comparator cost, one risk, Model A/B sentence | `## Model-choice memo` |
| Submission | - | README order: line 1 `Domain: Support`, How to run, Part 1-4 findings, Model-choice memo, Limitations (>= 3) | `## Limitations` |

Marks guard: a missing key/file/answer zeroes only that item; typing a reference value instead of computing scores zero for that line.

## 3. Constraints and rules from the brief

Repo and submission
- Single public repo, single branch `main`; submitted link is repo root (only if `main` is default) or `/tree/main`. Verify default branch is `main` before submitting.
- Required layout: `README.md`, `requirements.txt`, `generate_data.py`, `data/records.csv`, `part1.py`..`part4.py` (shared helper file allowed; importing it must not re-run a Part), `outputs/` with 4 results txt + 8 CSVs (see brief; note `part2_thresholds.csv`, `part2_knn_cv.csv`, `part3_segments.csv`, `part3_hierarchical.csv`, `part4_splits.csv`, `part4_voting.csv`, `part4_adaboost.csv`, `part4_architecture.csv`). Note `part3_results.txt` is required by Part 3 text and the layout lists it.
- README first line exactly `Domain: Support`; sections in the mandated order.

Forbidden / restricted
- No images, screenshots, PDFs, slides, video, audio committed.
- No other links in the repo/README (no notebooks, drives, apps, second repo).
- No paid/gated services, API keys, dataset downloads. Offline, Python stdlib + NumPy only (extra packages only for I/O or cross-checks, and must be pinned).
- No ready-made regression/KNN/k-means/PCA/metric routines for graded numbers (no `polyfit`, `cov`, `corrcoef`, `lstsq`); `numpy.linalg.solve` (T1.7) and `numpy.linalg.eigh` (T3.5) allowed.
- Do not edit generator constants or hand-edit `records.csv`. Do not type reference numbers. Original work; must be able to explain every line.
- Money in INR / "Rupees", never `$`.
- No Part may use a number it did not compute or receive from an earlier Part (except constants printed in brief).
- Test rows only evaluate; never fit, standardise, pick K or tau.

Format
- `key = value` lines; floats 4 dp, ints as ints, booleans `yes`/`no`; compute at full precision, round only on print. CSV exact headers, comma separator, floats 4 dp.
- Sample SD (n-1) everywhere; ln natural; positive means prob >= tau.
- Pinned conventions: stable sorts (argsort kind='stable'), tie rules (lower K, lower tau, lower centroid index), fold = position mod 5, K-means start rows and no iteration cap, PCA sign flip.
- Tolerances: default max(0.005, 0.0005*|ref|); confusion cells +/-1; cost_tau exact; gd_slope_gap < 0.001; n_required +/-1 half marks; money +/- INR 450.

Dates
- Window 6-16 Nov 2026 (11 days); submit before platform closing time. Today is 14 Nov 2026, so only about 3 days (14, 15, 16 Nov) remain; the suggested pace (P1 days 1-3, P2 4-6, P3 7-8, P4+README 9-11) is already behind and must be compressed (see section 7).

## 4. Assumptions and open questions

Assumptions
- A1: Python >= 3.10 and a NumPy version (1.26.4 or 2.2.6 preferred) are installable locally; pin whichever is used.
- A2: The GitHub repo exists or can be created by the student; default branch will be set to `main`.
- A3: A shared helper (e.g. `common.py`) is acceptable for data loading, split, standardisation, logistic model, metrics and result writer.
- A4: `outputs/part3_results.txt` is required (listed in layout and Part 3 intro).
- A5: Memo word count excludes the heading; keep it well under 300 to be safe.
- A6: Checkpoints (mean_value 8.9382, train 560/119, loss0 0.6931, wcss_k2 2262.6753, eigenvalue_sum 5.0000, root_entropy 0.7462, round1_error 0.2500, generator hash) are used only as sanity checks, never as inputs.

Open questions (to confirm with course staff or the student)
- Q1: Exact submission closing time on the platform (brief says "shown there"); with only 2-3 days left, the deadline hour matters.
- Q2: Is the git remote/repo already created, and under which account? (Not pushing in this task; remote to be added by the student.)
- Q3: Which NumPy version is installed locally (decides the `requirements.txt` pin)?
- Q4: Is `generate_data.py` already available as a file? Only embedded in the brief now; must be copied verbatim (watch for line-ending/whitespace changes that alter nothing in output but keep verbatim).
- Q5: Is a helper-file name constraint present? Brief says only "shared helper files are fine".
- Q6: Windows line endings: `records.csv` MD5 must match; csv module writes `\r\n` by default with `newline=""`; confirm hash on the student's OS and set `.gitattributes` (`* -text`, or `data/records.csv binary`) so git does not rewrite line endings.
- Q7: Per-item mark weights are unpublished; effort is allocated by Part marks and key counts.

## 5. Risks

| ID | Risk | Likelihood / impact | Mitigation |
|---|---|---|---|
| R1 | Time: about 3 days left of an 11-day window | High / High | Compress plan (section 7); build shared helper once; write README sections as each Part finishes; reserve final day for verification and submission |
| R2 | MD5 mismatch from line-ending conversion by git/Windows | Medium / High | Run generator on the target OS, verify printed hash, `.gitattributes` to stop EOL conversion, re-verify after a fresh clone |
| R3 | Pinned-convention slips (unstable sort, SD divisor, fold rule, tie-breaks, start centroids) shift numbers | High / High | Implement each convention literally; check all Checkpoints; assert in code for sizes/sums (segments = 800, cell counts consistent) |
| R4 | Using a forbidden routine (polyfit, cov, lstsq, etc.) | Low / High | Grep own code for banned calls before commit |
| R5 | Hard-coding reference numbers | Low / Critical | No literals for graded values; checkpoints only as asserts-free manual comparisons (or comparisons that never write the output) |
| R6 | Test-set leakage (standardising, K, tau) | Medium / High | Single `standardise(train)` function applied to test; K and tau chosen from train/CV only |
| R7 | Non-convergence/overflow in logistic (eta=1.0), log(0) in BCE | Medium / Medium | Stable sigmoid and clipped log used for loss only; verify epoch-0 loss = 0.6931 |
| R8 | K-means with 21-27 passes and empty-cluster edge case, tie rule | Medium / Medium | Follow pinned rules; compare pass counts (K=4: 21, K=5: 15, K=6: 27) as a self-check |
| R9 | Outputs not reproducible from a clean clone (order, paths, floats) | Medium / High | Run `generate_data.py` and part1-4 from a fresh clone and diff `outputs/` before submitting |
| R10 | README quotes numbers differing from committed outputs, or exceeds memo limit | Medium / Medium | Generate README figures by reading outputs; word-count the memo |
| R11 | Wrong branch / default branch not `main`; extra links; image files committed | Low / Critical | Submission checklist (section 6, M5) |
| R12 | Interpretation errors in text answers (Type I wording, funnel, overfit, vanishing gradient) | Medium / Medium | Short, number-backed answers following the R-item checklist |

## 6. Work breakdown and milestones

Lifecycle: Plan -> Design -> Implement -> Test -> Deploy. Each milestone has exit criteria. Milestones are ordered; Implement/Test run per Part so a Part is finished and verified before the next starts.

### M0 - Plan (this document)
Exit: PLAN.md committed; every deliverable mapped; open questions listed.

### M1 - Design (short; one sitting)
Tasks:
- D1: Fix repo skeleton and module boundaries (data/IO, split+standardise, logistic model, metrics, K-means, hierarchical, PCA, boosting, results writer) and the order of scripts for the README.
- D2: Decide shared helper contents and the contract that importing it has no side effects.
- D3: Design the output writer (4 dp floats, ints, yes/no) and CSV writer with exact headers.
- D4: Define the self-check list (all Checkpoints, row counts, cell-count/rate consistency, K-means pass counts) and the pre-submission verification script/procedure.
- D5: Outline README structure with placeholders per R-item.
Exit: written design notes (module list, function signatures at the level of names, conventions table) agreed; no unresolved convention ambiguity.

### M2 - Implement and Test, Part 0 and Part 1
Tasks: T0.1, T0.2, then Tasks 1.1-1.7, R1.1-R1.5.
Exit: generator prints the exact required line; `part1_results.txt` has all keys; checkpoints n=800 and mean_value=8.9382 match; tss = ess + rss = yes; gd_slope_gap < 0.001; stable sort used; README Part 1 section written from outputs.

### M3 - Implement and Test, Part 2
Tasks: 2.1-2.8, R2.1-R2.5.
Exit: 560/119/240/51 matches; loss_epoch_0 = 0.6931; thresholds CSV 9 rows, knn CV CSV 11 rows with exact headers; cost_tau is a multiple of 0.05; confusion cells sum to 240 and rates match cells; no test-set leakage; README Part 2 written.

### M4 - Implement and Test, Part 3
Tasks: 3.1-3.5, R3.1-R3.4.
Exit: wcss_k2 = 2262.6753; K=4/5/6 pass counts 21/15/27; segment sizes sum to 800; eigenvalue_sum = 5.0000; hierarchical CSV 15 rows with merges ordered correctly; PCA signs per convention; README Part 3 written.

### M5 - Implement and Test, Part 4 and memo
Tasks: 4.1-4.6, R4.1-R4.4, memo.
Exit: root_entropy = 0.7462; round1_error = 0.2500; CSV row counts 4/5/16/7; layer/parameter counts cross-checked by hand arithmetic; Part 4 reuses Part 2 model without re-running Part 2 on import; memo <= 300 words with >= 3 outputs numbers, tau, INR cost, comparator cost, a risk, A/B sentence.

### M6 - Test (integration)
Tasks: fresh-clone run of the full command sequence; diff regenerated `outputs/` against committed; grep for banned functions, `$` money symbols, image files, URLs; checklist each key name against the brief; README order and first line; `requirements.txt` pins; word count; Limitations (>= 3).
Exit: zero diffs after clean regeneration; all keys present; checklist signed off.

### M7 - Deploy (submission)
Tasks: add remote (student), push to `main` only, confirm default branch is `main`, open repo page in a private/incognito view to confirm public, confirm link form, submit before closing time.
Exit: link resolves to `main`, repo public, all required files visible, submission acknowledged.

## 7. Schedule (compressed, from today 14 Nov 2026)

| Day | Work |
|---|---|
| 14 Nov (today) | M0, M1, M2 (Part 0 + Part 1), start M3 |
| 15 Nov | Finish M3, M4 (Part 3), start M5 |
| 16 Nov | Finish M5, M6, M7; submit well before closing time; keep a buffer of several hours |

Because the window nominally ends 16 Nov, a fallback order of priority if time runs out: Part 2 (30) > Part 1 (25) = Part 3 (25) > Part 4 (20), while always keeping the repo valid (all files and headers present).

## 8. Proposed tech stack

- Python 3.10+ (stdlib: csv, math, hashlib, os); NumPy (1.26.4 or 2.2.6, pinned in `requirements.txt`).
- No extra packages planned; if any is used for cross-checking only, it is not committed in the pipeline (or is pinned if imported).
- Git (local, branch `main`), GitHub for hosting; `.gitattributes` to preserve the CSV bytes.
- Plain scripts: `generate_data.py`, a shared `common.py` helper, `part1.py`..`part4.py`; plain-text outputs. No notebooks, no plotting libraries.

## 9. Dependencies and data needed

- Data: `data/records.csv` produced by the verbatim generator (seed 2508, 800 rows, 170 positives). No external data.
- Constants supplied in the brief: planning mean 8.0, E = 0.5, z = 1.96, eta values, thresholds, costs INR 50 / INR 400, split rule, K candidates, the 6x6 dissimilarity table (Task 3.4), the 8-point AdaBoost table (Task 4.3), network sizes (Task 4.5), split candidates S1-S4.
- Cross-Part dependencies: Part 4 needs Part 2's split, standardisation, logistic model (tau 0.3) and KNN (best K); Part 3.5 needs Part 3.1 standardised matrix and Task 3.3 segments; Part 1.7 and 1.6 build on Task 1.4 fitted values; Task 2.8 needs Task 2.2 model; memo needs Task 2.8 outputs.
- Tooling: local Python install, `pip`, git; internet only for `pip install` and pushing to GitHub.
