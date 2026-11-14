export async function api(path, opts) {
  let res;
  try { res = await fetch(path, opts); } catch (e) { throw new Error("Network error: the server is not reachable."); }
  let body = null;
  try { body = await res.json(); } catch (e) { /* non-JSON error body */ }
  if (!res.ok) {
    let d = body && body.detail;
    if (Array.isArray(d)) d = d.map((x) => (x.loc || []).slice(1).join(".") + ": " + x.msg).join("; ");
    throw new Error(d || "Request failed (" + res.status + ")");
  }
  return body;
}
export const qs = (o) => new URLSearchParams(o).toString();
