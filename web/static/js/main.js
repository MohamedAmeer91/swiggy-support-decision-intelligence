import { api, qs } from "./api.js";
import { el, card, table, metricsTable, prose, slider, status, confusionView, kpis, inr, f4 } from "./ui.js";
import { lineChart, scatter, legend, barRows } from "./charts.js";

const ROUTES = [
  ["overview", "Overview"], ["part1", "Part 1"], ["part2", "Part 2"], ["part3", "Part 3"],
  ["part4", "Part 4"], ["score", "Score a ticket"], ["memo", "Memo and limits"],
];
const app = document.getElementById("app");
const nav = document.getElementById("nav");
const pct = (v) => (100 * v).toFixed(1) + "%";
const SEG_COLORS = { A: "var(--neutral)", B: "var(--ink)", C: "var(--accent)" };
let textCache = null;
const getText = async () => (textCache = textCache || (await api("/api/text")));

function clear(n) { while (n.firstChild) n.firstChild.remove(); }
const grid = (cls, ...k) => el("div", { class: "grid " + (cls || "") }, k);

// ------------------------------------------------------------------ overview
async function overview() {
  const d = await api("/api/overview");
  return [
    el("h1", {}, d.title),
    d.problem.map((p, i) => el("p", { class: i ? "muted" : "lead" }, p)),
    el("h2", {}, "Headline numbers"),
    grid("", d.headline.map((h) => card(el("div", { class: "stat" }, el("div", { class: "l" }, h.label),
      el("div", { class: "v" }, h.value), el("div", { class: "n" }, h.note))))),
    el("h2", {}, "Key findings"),
    card(el("ul", {}, d.findings.map((f) => el("li", {}, f)))),
    el("h2", {}, "Try it"),
    el("p", {}, "Open Part 2 to move the alert threshold and watch the INR cost, Part 3 to explore segments, "
      + "or Score a ticket to see a prediction for your own inputs."),
  ];
}

// ------------------------------------------------------------------ part 1
async function part1() {
  const [r, t] = await Promise.all([api("/api/results/1"), getText()]);
  const m = r.metrics;
  const keys = (re) => Object.keys(m).filter((k) => re.test(k));
  return [
    el("h1", {}, "Part 1. " + r.title),
    el("p", { class: "lead" }, "Is the 8 minute planning assumption right, and how well can a simple model explain resolution time?"),
    grid("two",
      card(metricsTable(m, ["n", "mean_value", "sd_value", "se_value", "ci95_low", "ci95_high", "z_stat", "reject_h0", "n_required"], "Mean test and sample size")),
      card(metricsTable(m, ["reg_slope", "reg_intercept", "r2", "rmse", "mae", "tss", "ess", "rss"], "Simple regression on account value")),
      card(metricsTable(m, keys(/^gd_/), "Gradient descent, same line")),
      card(metricsTable(m, keys(/^(loglog|resid)/), "Log-log model and residual spread")),
      card(metricsTable(m, keys(/^mr_/), "Multiple regression"))),
    el("h2", {}, "Findings"), card(prose(t["Part 1 findings"])),
  ];
}

// ------------------------------------------------------------------ part 2
async function part2() {
  const [r, t, meta] = await Promise.all([api("/api/results/2"), getText(), api("/api/meta")]);
  const st = { tau: 0.15, fp: meta.cost_fp, fn: meta.cost_fn, ds: "test", k: meta.best_k };
  const err = status();
  const cmBox = el("div"), kpiBox = el("div"), costBox = el("div"), rocBox = el("div"), costChart = el("div");
  let curveData = null, seq = 0;

  const dsSel = el("select", { id: "ds" }, el("option", { value: "test" }, "Test rows (240)"),
    el("option", { value: "train" }, "Training rows (560)"));
  dsSel.addEventListener("change", () => { st.ds = dsSel.value; refreshCurve(); });
  const costIn = (id, label, key) => {
    const i = el("input", { type: "number", id, min: 0, max: 100000, step: 10, value: st[key] });
    i.addEventListener("change", () => { st[key] = Math.max(0, Number(i.value) || 0); refreshCurve(); });
    return el("div", {}, el("label", { for: id }, label), i);
  };

  async function refreshCurve() {
    try {
      curveData = await api("/api/curve?" + qs({ dataset: st.ds, cost_fp: st.fp, cost_fn: st.fn }));
      err.clear();
    } catch (e) { err.show(e.message); return; }
    refreshPoint();
  }
  async function refreshPoint() {
    const my = ++seq;
    let d;
    try { d = await api("/api/threshold?" + qs({ tau: st.tau, dataset: st.ds, cost_fp: st.fp, cost_fn: st.fn })); err.clear(); }
    catch (e) { err.show(e.message); return; }
    if (my !== seq) return;
    clear(cmBox); cmBox.append(confusionView(d));
    clear(kpiBox); kpiBox.append(kpis([["accuracy", pct(d.accuracy)], ["precision", pct(d.precision)],
      ["recall", pct(d.recall)], ["F1", d.f1.toFixed(4)], ["false alarm rate", pct(d.fpr)]]));
    clear(costBox);
    costBox.append(kpis([["cost at this threshold", inr(d.cost)], ["cost at 0.5", inr(d.cost_at_0_5)],
      ["cost, flag nobody", inr(d.cost_flag_nobody)]]),
      el("p", { class: "muted" }, "Cost = " + d.cost_fp + " x false alarms + " + d.cost_fn + " x missed escalations. Lowest cost on this data is at threshold "
        + curveData.best_tau.toFixed(2) + " (" + inr(curveData.best_cost) + ")."));
    if (curveData) {
      const pts = curveData.points, cur = pts[Math.round(st.tau * 100)];
      clear(rocBox); rocBox.append(lineChart({ title: "ROC style curve", xl: "false positive rate", yl: "true positive rate",
        xd: [0, 1], yd: [0, 1], diagonal: true, series: [{ points: pts.map((p) => [p.fpr, p.tpr]) }], marker: [cur.fpr, cur.tpr] }));
      const mx = Math.max(...pts.map((p) => p.cost));
      clear(costChart); costChart.append(lineChart({ title: "Cost by threshold", xl: "threshold", yl: "cost (INR)",
        xd: [0, 1], yd: [0, mx], series: [{ points: pts.map((p) => [p.tau, p.cost]) }], marker: [cur.tau, cur.cost] }));
    }
  }

  const tauSlider = slider("tau", "Alert threshold", 0, 1, 0.01, st.tau, (v) => { st.tau = v; refreshPoint(); }, (v) => v.toFixed(2));
  const lab = card(
    el("h3", {}, "Threshold lab"),
    el("p", { class: "muted" }, "Flag a ticket for supervisor review when its predicted escalation probability is at least the threshold."),
    el("div", { class: "controls" }, tauSlider, el("div", {}, el("label", { for: "ds" }, "Evaluate on"), dsSel),
      costIn("cfp", "Cost of a false alarm (INR)", "fp"), costIn("cfn", "Cost of a missed escalation (INR)", "fn")),
    err.node,
    grid("two", el("div", {}, cmBox, kpiBox, costBox), el("div", {}, rocBox, costChart)));
  refreshCurve();

  // KNN
  const knnBox = el("div"), knnErr = status();
  const kSel = el("select", { id: "k" }, meta.knn_ks.map((k) => el("option", { value: k, selected: k === st.k ? "" : null }, "K = " + k)));
  async function loadKnn() {
    try {
      const d = await api("/api/knn?k=" + kSel.value); knnErr.clear(); clear(knnBox);
      knnBox.append(grid("two", el("div", {}, confusionView(d),
        kpis([["accuracy", pct(d.accuracy)], ["precision", pct(d.precision)], ["recall", pct(d.recall)], ["F1", d.f1.toFixed(4)]]),
        el("p", { class: "muted" }, "Cross-validated F1 for K = " + d.k + ": " + (d.cv_f1 == null ? "not computed" : d.cv_f1.toFixed(4))
          + ". CV picked K = " + d.best_k + ".")),
        el("div", {}, lineChart({ title: "Cross-validated F1 by K", xl: "K", yl: "mean CV F1", xd: [0, 22], yd: [0.3, 0.5],
          series: [{ points: d.cv.map((p) => [p.k, p.mean_cv_f1]), dots: true }], marker: d.cv_f1 == null ? null : [d.k, d.cv_f1] }))));
    } catch (e) { knnErr.show(e.message); }
  }
  kSel.addEventListener("change", loadKnn); loadKnn();

  const m = r.metrics;
  const w = [1, 2, 3, 4, 5, 6, 7].map((i) => ["X" + i + " weight", m["weight_X" + i]]);
  return [
    el("h1", {}, "Part 2. " + r.title),
    el("p", { class: "lead" }, "A logistic regression trained from scratch predicts which tickets escalate. Choose the alert threshold with money."),
    lab,
    el("h2", {}, "K-nearest neighbours"),
    card(el("div", { class: "controls" }, el("div", {}, el("label", { for: "k" }, "Number of neighbours"), kSel)), knnErr.node, knnBox),
    el("h2", {}, "Model and fixed results"),
    grid("two", card(el("h3", {}, "Standardised logistic weights"), barRows(w)),
      card(metricsTable(m, ["train_rows", "train_positives", "test_rows", "test_positives", "test_bce", "blind_accuracy", "cost_tau",
        "cost_train_at_tau", "cost_test_at_tau", "cost_test_at_0.5", "cost_test_flag_nobody"], "Run summary")),
      card(table(r.tables.thresholds, "Threshold sweep on test rows")),
      card(metricsTable(m, ["odds_ratio_X1", "odds_ratio_X2", "odds_ratio_X3", "odds_ratio_X4", "odds_ratio_X5", "odds_ratio_X6", "odds_ratio_X7"], "Odds ratios per standard deviation"))),
    el("h2", {}, "Findings"), card(prose(t["Part 2 findings"])),
  ];
}

// ------------------------------------------------------------------ part 3
async function part3() {
  const [r, t, d] = await Promise.all([api("/api/results/3"), getText(), api("/api/segments")]);
  const box = el("div"), sel = el("select", { id: "seg" }, el("option", { value: "all" }, "All segments"),
    ...["A", "B", "C"].map((s) => el("option", { value: s }, "Segment " + s)));
  const outSel = el("select", { id: "outc" }, el("option", { value: "all" }, "All tickets"),
    el("option", { value: "1" }, "Escalated only"), el("option", { value: "0" }, "Not escalated only"));
  function draw() {
    clear(box);
    const pts = d.points.filter((p) => (sel.value === "all" || p.segment === sel.value) && (outSel.value === "all" || String(p.outcome) === outSel.value))
      .map((p) => ({ x: p.pc1, y: p.pc2, g: p.segment }));
    const groups = {}; for (const k of "ABC") groups[k] = { color: SEG_COLORS[k] };
    box.append(el("p", { class: "muted" }, pts.length + " tickets shown"),
      scatter({ title: "Tickets on the first two principal components", xl: "PC1", yl: "PC2", points: pts, groups }),
      legend([["var(--neutral)", "Segment A"], ["var(--ink)", "Segment B"], ["var(--accent)", "Segment C"]]));
  }
  sel.addEventListener("change", draw); outSel.addEventListener("change", draw); draw();
  const wc = Object.entries(d.wcss).map(([k, v]) => [Number(k), v]);
  const prof = d.profiles;
  const rateRows = prof.rows.map((row) => [("Segment " + row[0]), row[7]]);
  return [
    el("h1", {}, "Part 3. " + r.title),
    el("p", { class: "lead" }, "K-means finds " + d.elbow_k + " ticket segments on five continuous predictors; PCA compresses them to two axes."),
    card(el("h3", {}, "Segment explorer"), el("div", { class: "controls" }, el("div", {}, el("label", { for: "seg" }, "Segment"), sel),
      el("div", {}, el("label", { for: "outc" }, "Outcome"), outSel)), box),
    el("h2", {}, "Segment profiles"),
    grid("two", card(table(prof, "Segment means and escalation rate")),
      card(el("h3", {}, "Escalation rate by segment"), barRows(rateRows))),
    el("h2", {}, "Choosing the number of segments"),
    grid("two", card(lineChart({ title: "Within-cluster sum of squares by K", xl: "K", yl: "WCSS", xd: [2, 6],
        yd: [0, Math.max(...wc.map((p) => p[1]))], series: [{ points: wc, dots: true }], marker: wc.find((p) => p[0] === d.elbow_k) })),
      card(el("h3", {}, "Variance explained by component"), barRows(d.explained_ratio.map((v, i) => ["PC" + (i + 1), v])),
        el("p", { class: "muted" }, "Loadings of PC1: " + d.loadings.features.map((f, i) => f.replace(/_/g, " ") + " " + d.loadings.pc1[i].toFixed(2)).join("; ")))),
    el("h2", {}, "Hierarchical clustering of six examples"), card(table(d.hierarchical, "Merge history")),
    el("h2", {}, "Findings"), card(prose(t["Part 3 findings"])),
  ];
}

// ------------------------------------------------------------------ part 4
async function part4() {
  const [r, t] = await Promise.all([api("/api/results/4"), getText()]);
  const box = el("div"), err = status();
  let seq = 0;
  async function load(tau) {
    const my = ++seq;
    try {
      const d = await api("/api/compare?tau=" + tau); if (my !== seq) return; err.clear(); clear(box);
      const best = d.models.reduce((a, b) => (b.cost < a.cost ? b : a));
      const rows = d.models.map((x) => [x.model, x.tp, x.fp, x.tn, x.fn, x.precision, x.recall, x.f1, x.cost]);
      box.append(table({ header: ["model", "tp", "fp", "tn", "fn", "precision", "recall", "f1", "cost INR"], rows }, "Test rows at threshold " + tau.toFixed(2),
        d.models.indexOf(best)), el("p", { class: "muted" }, "Highlighted row has the lowest cost. KNN always uses its own majority rule."));
      box.append(barRows(d.models.map((x) => [x.model + " F1", x.f1])));
    } catch (e) { err.show(e.message); }
  }
  load(0.3);
  const m = r.metrics;
  return [
    el("h1", {}, "Part 4. " + r.title),
    el("p", { class: "lead" }, "Which structured-data model should go to production, and how big are the neural networks a later project would need?"),
    card(el("h3", {}, "Model comparison and voting"),
      el("div", { class: "controls" }, slider("tau4", "Threshold for logistic, stump and soft vote", 0, 1, 0.01, 0.3, load, (v) => v.toFixed(2))), err.node, box),
    el("h2", {}, "Decision-tree splits"), grid("two", card(table(r.tables.splits, "Information and Gini gain, training rows")),
      card(metricsTable(m, ["root_entropy", "root_gini", "best_split_by_info_gain", "best_split_by_gini_gain", "stump_rate_yes", "stump_rate_no", "oob_fraction"], "Tree facts"))),
    el("h2", {}, "Boosting by hand"), grid("two", card(table(r.tables.adaboost, "AdaBoost point weights")),
      card(metricsTable(m, ["round1_error", "round1_alpha", "round2_error", "round2_alpha", "ensemble_accuracy"], "Boosting rounds"))),
    el("h2", {}, "Network sizing"), grid("two", card(table(r.tables.architecture, "Parameters per layer")),
      card(metricsTable(m, ["mlp_total", "cnn_total", "fc_layer_params", "conv_layer_params", "rnn_total"], "Totals"))),
    el("h2", {}, "Findings"), card(prose(t["Part 4 findings"])),
  ];
}

// ------------------------------------------------------------------ score a ticket
const LABELS = {
  customer_tenure_months: "Customer tenure (months)", earlier_ticket_count_90d: "Earlier tickets, last 90 days",
  sla_consumed_ratio: "Share of response target used (0 to 1+)", account_value_inr_thousands: "Account value (INR thousands)",
  satisfaction_score: "Satisfaction score (0 to 100)", reopened_flag: "Reopened before", self_service_first_flag: "Tried self-service first",
};
async function scoreView() {
  const meta = await api("/api/meta");
  const err = status(), out = el("div", { "aria-live": "polite" });
  const inputs = {};
  const fields = meta.features.map((f) => {
    let i;
    if (f.binary) {
      i = el("select", { id: f.name }, el("option", { value: 0 }, "No"), el("option", { value: 1 }, "Yes"));
    } else {
      i = el("input", { type: "number", id: f.name, min: 0, step: "any", value: f.mean });
    }
    inputs[f.name] = i;
    return el("div", {}, el("label", { for: f.name }, LABELS[f.name]), i,
      f.binary ? null : el("span", { class: "muted" }, "Data range " + f.min + " to " + f.max));
  });
  const tau = el("input", { type: "number", id: "tau5", min: 0, max: 1, step: 0.01, value: 0.15 });
  async function run(ev) {
    ev.preventDefault();
    const body = { tau: Number(tau.value) };
    for (const f of meta.features) body[f.name] = Number(inputs[f.name].value);
    try {
      const d = await api("/api/score", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      err.clear(); clear(out);
      out.append(el("h3", {}, "Predicted escalation probability: " + pct(d.probability)),
        el("p", {}, el("span", { class: "pill" }, d.flagged ? "Flag for supervisor review" : "No review needed"),
          " at threshold " + d.tau.toFixed(2)),
        kpis([["expected cost if flagged", inr(d.expected_cost_flag)], ["expected cost if skipped", inr(d.expected_cost_skip)]]),
        el("h3", {}, "What moved the score"),
        el("p", { class: "muted" }, "Each bar is weight x standardised value, added to the intercept " + d.bias.toFixed(3) + "."),
        barRows(d.contributions.map((c) => [LABELS[c.feature].replace(/ \(.*\)/, ""), c.effect])));
    } catch (e) { err.show(e.message); }
  }
  const form = el("form", { onsubmit: run }, el("div", { class: "controls" }, fields,
    el("div", {}, el("label", { for: "tau5" }, "Alert threshold"), tau)), el("button", { type: "submit" }, "Score ticket"));
  return [
    el("h1", {}, "Score a ticket"),
    el("p", { class: "lead" }, "Enter the seven predictors for one ticket. The trained logistic weights return an escalation probability."),
    card(form, err.node, out),
  ];
}

// ------------------------------------------------------------------ memo
async function memo() {
  const t = await getText();
  return [el("h1", {}, "Model-choice memo"), card(prose(t["Model-choice memo"])),
    el("h2", {}, "Limitations"), card(prose(t["Limitations"].replace(/\n(?=\d+\. )/g, "\n\n")))];
}

const PAGES = { overview, part1, part2, part3, part4, score: scoreView, memo };

async function route() {
  const name = (location.hash.replace(/^#\//, "") || "overview");
  const page = PAGES[name] || overview;
  const key = PAGES[name] ? name : "overview";
  clear(nav);
  ROUTES.forEach(([k, label]) => nav.append(el("a", { href: "#/" + k, "aria-current": k === key ? "page" : null }, label)));
  clear(app); app.append(el("p", { class: "muted" }, "Loading"));
  try {
    const content = await page();
    clear(app); app.append(...[content].flat(5));
    document.title = (ROUTES.find((r) => r[0] === key)[1]) + " | Swiggy Support Decision Intelligence";
  } catch (e) {
    clear(app); app.append(el("div", { class: "alert", role: "alert" }, "Could not load this page. " + e.message));
  }
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);
route();
