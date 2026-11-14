# Web layer design

## Module layout
```
web/
  app.py            FastAPI app, routes, static mount
  service.py        model state (cached at startup) and pure calculation functions
  schemas.py        pydantic request and response models
  outputs_io.py     parsers for outputs/*.txt, *.csv and README sections
  static/
    index.html      shell, nav, theme tokens link
    css/style.css   tokens, layout, components, light and dark
    js/main.js      router, page renderers
    js/api.js       fetch wrapper with error handling
    js/charts.js    inline SVG line, bar and scatter helpers
    js/ui.js        DOM helpers (el(), table(), card())
  tests/            unittest + TestClient
  docs/ README.md Dockerfile requirements.txt
```
`service.py` puts the repo root on `sys.path`, imports `common` only (no side effects) and never writes.
K-means and PCA are re-implemented in `service.py` with the same pinned rules as Part 3 and checked
against `outputs/part3_*` in tests.

## API schema (JSON)
- Metric: `{ "key": str, "value": number|string }`; Table: `{ "header": [str], "rows": [[...]] }`.
- GET /api/threshold -> `{dataset, tau, cost_fp, cost_fn, tp, fp, tn, fn, accuracy, precision, recall, f1, specificity, fpr, tpr, cost, cost_flag_nobody, cost_at_0_5, n, positives}`.
  Query: tau in [0,1], cost_fp and cost_fn in [0,100000] (defaults 50 and 400), dataset in train|test (default test).
- GET /api/curve -> `{dataset, points: [{tau, tpr, fpr, cost}], best_tau, best_cost}` for tau = 0.00..1.00 step 0.01.
- GET /api/knn?k (odd 1..41) -> `{k, tp, fp, tn, fn, accuracy, precision, recall, f1, cv_f1|null, best_k, cv: [{k, mean_cv_f1}]}`.
- GET /api/segments -> `{profiles: [...], wcss: {k: v}, elbow_k, explained_ratio: [..], loadings: {...}, points: [{pc1, pc2, segment, outcome}], hierarchical: Table}`.
- GET /api/compare?tau -> `{tau, models: [{model, tp, fp, tn, fn, precision, recall, f1, cost}]}`.
- POST /api/score body `{customer_tenure_months, earlier_ticket_count_90d, sla_consumed_ratio, account_value_inr_thousands, satisfaction_score, reopened_flag, self_service_first_flag, tau?}`
  -> `{probability, flagged, tau, contributions: [{feature, z, weight, effect}], bias, expected_cost_flag, expected_cost_skip}`.
- GET /api/results/{part} -> `{part, title, metrics: {key: value}, tables: {name: Table}}`.
- GET /api/overview, /api/meta, /api/text, /api/health.
- Errors: FastAPI default `{ "detail": ... }` with 422 for bad input, 404 for unknown part; the
  frontend shows `detail` in an inline alert.

## Frontend structure
Hash router (`#/overview`, `#/part1` ... `#/score`, `#/memo`). Each page is a function that
fetches its endpoints and builds DOM with `textContent` only (no innerHTML with data, so no
injection). Controls debounce 80 ms before calling the API; the previous result stays visible
with an aria-live status line while loading. Charts are inline SVG with titles, axis labels and
a text table alternative where it fits.

## Visual design
Shared portfolio look: neutral background, one accent (Swiggy-leaning orange, a darker tone for
text on light, lighter tone on dark to keep contrast of at least 4.5:1), white cards with a
1px border and 12px radius, system font stack, 16px base, 1.6 line height, max width 1080px,
sticky top nav that wraps on phones. Tokens are CSS variables on `:root`; dark values under
`@media (prefers-color-scheme: dark)`. Positive/negative classes use the accent plus a neutral
grey (never colour alone: labels and values are always printed). Focus rings are visible;
sliders have labels and live value text; reduced-motion respected.
