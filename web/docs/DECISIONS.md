# Decisions

1. Single-page app with hash routes; plain ES modules, no build step, no vendored library. Charts are
   inline SVG written in `charts.js`, so nothing external is loaded and the page works offline.
2. The web layer imports only `common.py`. K-means and PCA are re-implemented in `service.py` with the
   Part 3 rules (rather than importing `part3.py`) and tests check them against `outputs/part3_*`.
3. Tables and headline numbers are read from `outputs/`; interactive numbers are computed from the same
   trained model via `common.part2_pipeline()` once at startup (about half a second).
4. Threshold lab uses the brief's cost rule (INR 50 per false alarm, 400 per miss) as defaults; the two
   costs are editable. The curve is a 0.00 to 1.00 grid in steps of 0.01; the lab can evaluate on test or training rows.
5. KNN selector offers odd K from 1 to 41 (odd avoids tied votes); CV F1 exists only for K up to 21, so the
   response returns null beyond that and the UI says so.
6. Part 4 comparison reproduces the voting rules (logistic, KNN, tenure stump, hard and soft vote) with a
   user threshold. The stump is split S4 (tenure at most 24), confirmed by `best_split_by_info_gain`.
7. Score form: inputs are validated by pydantic against generous plausible ranges; contributions are weight times
   standardised value using training-row mean and SD. Default threshold 0.15 (the chosen cost-based one).
8. Memo, findings and limitations are read from the root README at request time (cached by mtime) so the
   site never drifts from the submitted text.
9. The root `.gitignore` ignores `tests/`; `web/.gitignore` re-includes `web/tests/` so the root is not edited.
10. Text from files is inserted with textContent / DOM nodes only; a tiny inline renderer supports bold and code.
11. Pinned: fastapi 0.115.6, uvicorn 0.34.0, httpx 0.28.1, pydantic 2.14.3 (numpy stays at the root pin).
