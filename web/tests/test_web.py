"""Web layer tests. Run from the repo root: python -m unittest discover -s web/tests -t .
Numbers are cross-checked against the committed files in outputs/."""
import csv
import os
import unittest

from fastapi.testclient import TestClient

from web.app import app

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def results(name):
    out = {}
    with open(os.path.join(ROOT, "outputs", name)) as f:
        for line in f:
            k, v = line.strip().split(" = ")
            out[k] = v
    return out


def table(name):
    with open(os.path.join(ROOT, "outputs", name)) as f:
        return list(csv.DictReader(f))


GOOD = dict(customer_tenure_months=20, earlier_ticket_count_90d=3, sla_consumed_ratio=0.7,
            account_value_inr_thousands=10, satisfaction_score=60, reopened_flag=1, self_service_first_flag=0)


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = TestClient(app)
        cls.c = cls.ctx.__enter__()  # runs the startup lifespan

    @classmethod
    def tearDownClass(cls):
        cls.ctx.__exit__(None, None, None)

    def get(self, url, code=200):
        r = self.c.get(url)
        self.assertEqual(r.status_code, code, r.text)
        return r.json()

    # ---------------------------------------------------------------- basics
    def test_health_and_meta(self):
        self.assertEqual(self.get("/api/health"), {"status": "ok"})
        m = self.get("/api/meta")
        self.assertEqual((m["rows"], m["train_rows"], m["test_rows"]), (800, 560, 240))
        self.assertEqual(len(m["features"]), 7)
        self.assertEqual(m["best_k"], int(results("part2_results.txt")["knn_best_k"]))

    def test_overview(self):
        d = self.get("/api/overview")
        self.assertEqual(len(d["headline"]), 6)
        self.assertTrue(d["findings"] and d["problem"])
        text = " ".join(h["value"] + h["note"] for h in d["headline"])
        self.assertIn("%.2f" % float(results("part1_results.txt")["mean_value"]), text)
        self.assertIn("INR " + results("part2_results.txt")["cost_test_at_tau"], text)

    def test_results_parts(self):
        for part, n_tables in ((1, 0), (2, 2), (3, 2), (4, 4)):
            d = self.get("/api/results/%d" % part)
            self.assertEqual(d["part"], part)
            self.assertEqual(len(d["tables"]), n_tables)
            self.assertTrue(d["metrics"])
        m = self.get("/api/results/2")["metrics"]
        self.assertEqual(m["tau_0.5_tp"], 24)
        self.assertAlmostEqual(m["weight_X3"], float(results("part2_results.txt")["weight_X3"]))
        self.get("/api/results/5", 404)
        self.get("/api/results/abc", 422)

    def test_text(self):
        d = self.get("/api/text")
        self.assertEqual(len(d), 6)
        self.assertIn("logistic", d["Model-choice memo"].lower())
        self.assertTrue(d["Limitations"])

    # ---------------------------------------------------------------- threshold lab
    def test_threshold_matches_part2(self):
        r = results("part2_results.txt")
        for tau in ("0.5", "0.3"):
            d = self.get("/api/threshold?tau=" + tau)
            for k in ("tp", "fp", "tn", "fn"):
                self.assertEqual(d[k], int(r["tau_%s_%s" % (tau, k)]), k)
            for k in ("accuracy", "precision", "recall", "f1", "specificity"):
                self.assertAlmostEqual(d[k], float(r["tau_%s_%s" % (tau, k)]), places=3)
        self.assertEqual(d["cost"], 50 * d["fp"] + 400 * d["fn"])

    def test_threshold_costs_match_part2(self):
        r = results("part2_results.txt")
        t = self.get("/api/threshold?tau=%s&dataset=train" % r["cost_tau"])
        self.assertEqual(t["cost"], int(r["cost_train_at_tau"]))
        t = self.get("/api/threshold?tau=%s" % r["cost_tau"])
        self.assertEqual(t["cost"], int(r["cost_test_at_tau"]))
        self.assertEqual(t["cost_at_0_5"], int(r["cost_test_at_0.5"]))
        self.assertEqual(t["cost_flag_nobody"], int(r["cost_test_flag_nobody"]))

    def test_threshold_custom_costs(self):
        d = self.get("/api/threshold?tau=0.5&cost_fp=10&cost_fn=100")
        self.assertEqual(d["cost"], 10 * 20 + 100 * 27)

    def test_threshold_sweep_matches_csv(self):
        for row in table("part2_thresholds.csv"):
            d = self.get("/api/threshold?tau=" + row["tau"])
            for k in ("tp", "fp", "tn", "fn"):
                self.assertEqual(d[k], int(row[k]), (row["tau"], k))

    def test_curve(self):
        d = self.get("/api/curve")
        self.assertEqual(len(d["points"]), 101)
        self.assertEqual(d["points"][0]["tpr"], 1.0)
        self.assertEqual(d["points"][-1]["tpr"], 0.0)
        by = {round(p["tau"], 2): p for p in d["points"]}
        for row in table("part2_thresholds.csv"):
            p = by[round(float(row["tau"]), 2)]
            self.assertAlmostEqual(p["tpr"], float(row["tpr"]), places=3)
            self.assertAlmostEqual(p["fpr"], float(row["fpr"]), places=3)
        self.assertLessEqual(d["best_cost"], by[0.5]["cost"])

    def test_threshold_validation(self):
        for q in ("tau=1.5", "tau=-0.1", "tau=abc", "dataset=val", "cost_fp=-5", "cost_fn=1e9"):
            self.get("/api/threshold?" + q, 422)

    # ---------------------------------------------------------------- knn
    def test_knn(self):
        r = results("part2_results.txt")
        d = self.get("/api/knn?k=5")
        for k in ("tp", "fp", "tn", "fn"):
            self.assertEqual(d[k], int(r["knn_" + k]))
        self.assertAlmostEqual(d["f1"], float(r["knn_f1"]), places=3)
        cv = {row["K"]: float(row["mean_cv_f1"]) for row in table("part2_knn_cv.csv")}
        for p in d["cv"]:
            self.assertAlmostEqual(p["mean_cv_f1"], cv[str(p["k"])], places=3)
        self.assertEqual(self.get("/api/knn?k=7")["k"], 7)
        self.assertIsNone(self.get("/api/knn?k=31")["cv_f1"])

    def test_knn_validation(self):
        for q in ("k=4", "k=0", "k=43", "k=x"):
            self.get("/api/knn?" + q, 422)

    # ---------------------------------------------------------------- segments
    def test_segments(self):
        d = self.get("/api/segments")
        res = results("part3_results.txt")
        self.assertEqual(d["elbow_k"], int(res["elbow_k"]))
        self.assertEqual(len(d["points"]), 800)
        for s in "ABC":
            self.assertEqual(d["segment_sizes"][s], int(res["size_segment_" + s]))
        self.assertEqual(d["profiles"]["header"][0], "segment")
        for k in range(2, 7):
            self.assertAlmostEqual(d["wcss"][str(k)], float(res["wcss_k%d" % k]), places=3)
        for i, v in enumerate(d["explained_ratio"]):
            self.assertAlmostEqual(v, float(res["explained_ratio_%d" % (i + 1)]), places=3)
        for j in range(5):
            self.assertAlmostEqual(d["loadings"]["pc1"][j], float(res["pc1_loading_X%d" % (j + 1)]), places=3)
        self.assertEqual(len(d["hierarchical"]["rows"]), 15)

    # ---------------------------------------------------------------- compare
    def test_compare_matches_part4(self):
        d = self.get("/api/compare?tau=0.3")
        by = {m["model"]: m for m in d["models"]}
        for row in table("part4_voting.csv"):
            m = by[row["model"]]
            for k in ("tp", "fp", "tn", "fn"):
                self.assertEqual(m[k], int(row[k]), (row["model"], k))
            self.assertAlmostEqual(m["f1"], float(row["f1"]), places=3)
        self.get("/api/compare?tau=2", 422)
        self.assertEqual(len(self.get("/api/compare?tau=0.1")["models"]), 5)

    # ---------------------------------------------------------------- score
    def test_score(self):
        r = self.c.post("/api/score", json=GOOD)
        self.assertEqual(r.status_code, 200, r.text)
        d = r.json()
        self.assertTrue(0 < d["probability"] < 1)
        self.assertEqual(len(d["contributions"]), 7)
        import math
        logit = d["bias"] + sum(c["effect"] for c in d["contributions"])
        self.assertAlmostEqual(d["probability"], 1 / (1 + math.exp(-logit)), places=9)
        self.assertEqual(d["flagged"], d["probability"] >= d["tau"])
        hi = dict(GOOD, sla_consumed_ratio=1.5)
        self.assertGreater(self.c.post("/api/score", json=hi).json()["probability"], d["probability"])

    def test_score_validation(self):
        bad = [dict(GOOD, reopened_flag=2), dict(GOOD, sla_consumed_ratio=-1), dict(GOOD, tau=1.2),
               dict(GOOD, satisfaction_score="high"), {k: v for k, v in GOOD.items() if k != "reopened_flag"}, {}]
        for body in bad:
            self.assertEqual(self.c.post("/api/score", json=body).status_code, 422, body)
        self.assertEqual(self.c.post("/api/score", content="not json",
                                     headers={"Content-Type": "application/json"}).status_code, 422)

    # ---------------------------------------------------------------- static
    def test_static_served(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers["content-type"])
        self.assertIn("Swiggy Support", r.text)
        for p, ct in (("/static/css/style.css", "css"), ("/static/js/main.js", "javascript"),
                      ("/static/js/charts.js", "javascript"), ("/static/js/ui.js", "javascript"),
                      ("/static/js/api.js", "javascript")):
            r = self.c.get(p)
            self.assertEqual(r.status_code, 200, p)
            self.assertIn(ct, r.headers["content-type"])
        self.assertEqual(self.c.get("/static/nope.js").status_code, 404)
        self.assertIn("prefers-color-scheme: dark", self.c.get("/static/css/style.css").text)

    def test_read_only_numbers_unchanged(self):
        # the service never writes into outputs/: file contents identical before and after calls
        path = os.path.join(ROOT, "outputs", "part2_results.txt")
        def rd():
            with open(path, "rb") as f:
                return f.read()
        before = rd()
        self.get("/api/threshold?tau=0.2")
        self.assertEqual(before, rd())


if __name__ == "__main__":
    unittest.main()
