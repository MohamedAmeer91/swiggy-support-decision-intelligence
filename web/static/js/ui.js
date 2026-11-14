export function el(tag, attrs, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) n.setAttribute(k, v);
  }
  for (const c of kids.flat()) if (c != null) n.append(c.nodeType ? c : document.createTextNode(String(c)));
  return n;
}
export const f4 = (v) => (typeof v === "number" && !Number.isInteger(v) ? v.toFixed(4) : String(v));
export const inr = (v) => "INR " + Math.round(v).toLocaleString("en-IN");

export function card(...kids) { return el("div", { class: "card" }, kids); }

export function table(t, caption, hlRow) {
  const tb = el("table", {}, caption ? el("caption", {}, caption) : null,
    el("thead", {}, el("tr", {}, t.header.map((h) => el("th", { scope: "col" }, h)))),
    el("tbody", {}, t.rows.map((r, i) => el("tr", { class: hlRow === i ? "hl" : "" }, r.map((c) => el("td", {}, f4(c)))))));
  return el("div", { class: "tbl" }, tb);
}

export function metricsTable(m, keys, caption) {
  return table({ header: ["key", "value"], rows: keys.filter((k) => k in m).map((k) => [k, m[k]]) }, caption);
}

// minimal inline markup: **bold** and `code`, built with DOM nodes only
export function inline(text) {
  const out = [];
  text.split(/(\*\*[^*]+\*\*|`[^`]+`)/).forEach((p) => {
    if (p.startsWith("**")) out.push(el("strong", {}, p.slice(2, -2)));
    else if (p.startsWith("`")) out.push(el("code", {}, p.slice(1, -1)));
    else if (p) out.push(p);
  });
  return out;
}
export function prose(text) {
  return el("div", { class: "prose" }, text.split(/\n\s*\n/).map((p) => el("p", {}, inline(p.replace(/\n/g, " ")))));
}

export function slider(id, label, min, max, step, value, onInput, fmt) {
  const f = fmt || String;
  const show = el("span", { class: "val" }, f(value));
  const input = el("input", { type: "range", id, min, max, step, value });
  let t;
  input.addEventListener("input", () => {
    show.textContent = f(Number(input.value));
    clearTimeout(t);
    t = setTimeout(() => onInput(Number(input.value)), 80);
  });
  return el("div", {}, el("label", { for: id }, label + ": ", show), input);
}

export function status() {
  const n = el("div", { class: "alert", role: "alert", hidden: "" });
  return { node: n, show(msg) { n.textContent = msg; n.hidden = false; }, clear() { n.hidden = true; } };
}

export function confusionView(d) {
  const cell = (k, label, hit) => el("div", { class: "cell" + (hit ? " hit" : "") }, el("b", {}, d[k]), label);
  return el("div", { class: "cm", role: "group", "aria-label": "Confusion matrix" },
    el("div", { class: "hd" }, ""), el("div", { class: "hd" }, "Flagged"), el("div", { class: "hd" }, "Not flagged"),
    el("div", { class: "hd" }, "Escalated"), cell("tp", "caught (tp)", true), cell("fn", "missed (fn)"),
    el("div", { class: "hd" }, "Did not"), cell("fp", "false alarm (fp)"), cell("tn", "correct skip (tn)", true));
}

export function kpis(items) {
  return el("div", { class: "kpis" }, items.map(([l, v]) => el("div", {}, el("b", {}, v), el("span", {}, l))));
}
