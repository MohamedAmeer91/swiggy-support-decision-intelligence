const NS = "http://www.w3.org/2000/svg";
const s = (tag, attrs, text) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs || {})) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
};
export const COLORS = ["var(--accent)", "var(--ink)", "var(--neutral)"];
const W = 520, H = 320, M = { l: 52, r: 14, t: 14, b: 44 };

function frame(title, xl, yl, xd, yd) {
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart", role: "img", "aria-label": title });
  svg.append(s("title", {}, title));
  const X = (v) => M.l + ((v - xd[0]) / (xd[1] - xd[0] || 1)) * (W - M.l - M.r);
  const Y = (v) => H - M.b - ((v - yd[0]) / (yd[1] - yd[0] || 1)) * (H - M.t - M.b);
  const ticks = (d, n) => Array.from({ length: n + 1 }, (_, i) => d[0] + ((d[1] - d[0]) * i) / n);
  const fmt = (v) => (Math.abs(v) >= 100 ? Math.round(v) : +v.toFixed(2));
  ticks(yd, 4).forEach((v) => {
    svg.append(s("line", { x1: M.l, x2: W - M.r, y1: Y(v), y2: Y(v), stroke: "var(--grid)" }));
    svg.append(s("text", { x: M.l - 6, y: Y(v) + 4, "text-anchor": "end" }, fmt(v)));
  });
  ticks(xd, 5).forEach((v) => svg.append(s("text", { x: X(v), y: H - M.b + 16, "text-anchor": "middle" }, fmt(v))));
  svg.append(s("text", { x: (M.l + W - M.r) / 2, y: H - 6, "text-anchor": "middle" }, xl));
  svg.append(s("text", { x: 12, y: H / 2, "text-anchor": "middle", transform: `rotate(-90 12 ${H / 2})` }, yl));
  return { svg, X, Y };
}

export function lineChart({ title, xl, yl, xd, yd, series, marker, diagonal }) {
  const { svg, X, Y } = frame(title, xl, yl, xd, yd);
  if (diagonal) svg.append(s("line", { x1: X(0), y1: Y(0), x2: X(1), y2: Y(1), stroke: "var(--neutral)", "stroke-dasharray": "4 4" }));
  series.forEach((se, i) => {
    const d = se.points.map((p, j) => (j ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1)).join("");
    svg.append(s("path", { d, fill: "none", stroke: se.color || COLORS[i], "stroke-width": 2.2 }));
    if (se.dots) se.points.forEach((p) => svg.append(s("circle", { cx: X(p[0]), cy: Y(p[1]), r: 3.5, fill: se.color || COLORS[i] })));
  });
  if (marker) {
    svg.append(s("circle", { cx: X(marker[0]), cy: Y(marker[1]), r: 7, fill: "var(--accent)", stroke: "var(--card)", "stroke-width": 2 }));
  }
  return svg;
}

export function scatter({ title, xl, yl, points, groups }) {
  const pad = (a) => [Math.floor(Math.min(...a)), Math.ceil(Math.max(...a))];
  const { svg, X, Y } = frame(title, xl, yl, pad(points.map((p) => p.x)), pad(points.map((p) => p.y)));
  points.forEach((p) => {
    const g = groups[p.g];
    svg.append(s("circle", { cx: X(p.x), cy: Y(p.y), r: 3.2, fill: g.color, "fill-opacity": 0.6, stroke: g.color }));
  });
  return svg;
}

export function legend(items) {
  const d = document.createElement("div");
  d.className = "legend";
  items.forEach(([c, t]) => {
    const i = document.createElement("i"); i.style.background = c;
    const sp = document.createElement("span"); sp.append(i, t); d.append(sp);
  });
  return d;
}

export function barRows(rows) {
  const d = document.createElement("div");
  d.className = "bars";
  const m = Math.max(...rows.map((r) => Math.abs(r[1])), 1e-9);
  rows.forEach(([label, v]) => {
    const row = document.createElement("div"); row.className = "row";
    const l = document.createElement("span"); l.textContent = label;
    const tr = document.createElement("div"); tr.className = "track";
    const f = document.createElement("div"); f.className = "fill" + (v < 0 ? " neg" : "");
    const w = (Math.abs(v) / m) * 50;
    f.style.width = w + "%"; f.style.left = v < 0 ? 50 - w + "%" : "50%";
    tr.append(f);
    const val = document.createElement("span"); val.textContent = String(+v.toFixed(3));
    row.append(l, tr, val); d.append(row);
  });
  return d;
}
