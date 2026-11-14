# Web layer plan

## Purpose
An interactive portfolio page for the Swiggy support decision-intelligence project. It shows
the results already committed in `outputs/` and lets a visitor play with the model: move the
alert threshold and watch the confusion matrix and INR cost change, pick K for the nearest-
neighbour model, explore the three ticket segments, compare the Part 4 models and score a
ticket. The graded code and outputs are never modified; the web layer only reads `outputs/`
and imports helpers from `common.py`.

## Pages (single page app, hash routes, no build step)
1. Overview: problem statement, headline numbers, key findings.
2. Part 1: estimation and regression tables (mean test, sample size, regression fits).
3. Part 2: classifier. Interactive threshold lab (slider, confusion matrix, precision / recall /
   F1, ROC curve with current point, cost curve), KNN K selector with CV table, weights and odds ratios.
4. Part 3: segment explorer (PC1 / PC2 scatter coloured by segment, segment profile table),
   elbow chart, PCA variance, hierarchical merge tables.
5. Part 4: split gains, model comparison with threshold control (logistic, KNN, stump, hard and
   soft vote), AdaBoost weights, architecture parameter counts.
6. Score a ticket: form of the 7 features, predicted escalation probability, per-feature
   contribution, flag decision and expected cost.
7. Model-choice memo and Limitations, taken from the root README.

## API endpoints (JSON, all under /api)
- GET /api/health, GET /api/meta (features, ranges, defaults, cost rule)
- GET /api/overview
- GET /api/results/{part} for part 1 to 4 (key/value metrics and CSV tables)
- GET /api/threshold?tau&cost_fp&cost_fn&dataset (live confusion, rates, cost)
- GET /api/curve?dataset&cost_fp&cost_fn (ROC points and cost per tau)
- GET /api/knn?k (test confusion and rates for K, CV table)
- GET /api/segments (profiles, PCA, scatter points, elbow)
- GET /api/compare?tau (Part 4 model comparison at a threshold)
- POST /api/score (validated record, returns probability)
- GET /api/text (memo, limitations, findings from README)

## Data flow
Startup: load data, run `common.part2_pipeline()` once, compute test and train probabilities
for the logistic model and for KNN, compute K-means segments and PCA. Cache everything in
module state. Requests are pure functions over the cache plus parsed `outputs/` files
(parsed on demand, cached by file mtime). The frontend fetches JSON and draws charts as inline SVG.

## Scope
In: everything above, tests, Dockerfile, README. Out: authentication, a database, retraining
from the UI, any change to graded files, any network call at runtime.
