"""FastAPI app for the interactive portfolio layer. Run: uvicorn web.app:app"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import outputs_io as io
from . import service
from .schemas import ScoreRequest, ScoreResponse, ThresholdResponse

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

PARTS = {
    1: ("Estimation, inference and regression baseline", "part1_results.txt", []),
    2: ("Classification and evaluation", "part2_results.txt", ["part2_thresholds.csv", "part2_knn_cv.csv"]),
    3: ("Segmentation and dimensionality reduction", "part3_results.txt",
        ["part3_segments.csv", "part3_hierarchical.csv"]),
    4: ("Model-choice and architecture", "part4_results.txt",
        ["part4_splits.csv", "part4_voting.csv", "part4_adaboost.csv", "part4_architecture.csv"]),
}


@asynccontextmanager
async def lifespan(app):
    service.state()  # train and cache once at startup
    yield


app = FastAPI(title="Swiggy Support Decision Intelligence", version="1.0.0", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    return service.meta()


@app.get("/api/overview")
def overview():
    p1, p2, p3, p4 = (io.results("part%d_results.txt" % i) for i in (1, 2, 3, 4))
    headline = [
        {"label": "Mean resolution time", "value": "%.2f min" % p1["mean_value"],
         "note": "against a planning figure of 8 minutes"},
        {"label": "Test cost at chosen threshold", "value": "INR %d" % p2["cost_test_at_tau"],
         "note": "threshold %.2f, versus INR %d at 0.5" % (p2["cost_tau"], p2["cost_test_at_0.5"])},
        {"label": "Cost of flagging nobody", "value": "INR %d" % p2["cost_test_flag_nobody"],
         "note": "%d escalations among %d test tickets" % (p2["test_positives"], p2["test_rows"])},
        {"label": "Segments found", "value": str(p3["elbow_k"]),
         "note": "sizes %d / %d / %d" % (p3["size_segment_A"], p3["size_segment_B"], p3["size_segment_C"])},
        {"label": "Best K for KNN", "value": str(p2["knn_best_k"]), "note": "5-fold CV on training rows"},
        {"label": "Text model size", "value": "{:,}".format(p4["rnn_total"]),
         "note": "parameters, the sizing for a ticket-text network"},
    ]
    findings = [
        "The planning assumption of 8 minutes is rejected: the sample mean is %.2f minutes (z = %.2f) and "
        "about %d tickets would be needed for a 0.5 minute margin." % (p1["mean_value"], p1["z_stat"], p1["n_required"]),
        "Resolution time is far better modelled on a log scale: R-squared rises from %.2f to %.2f and the "
        "residual funnel disappears." % (p1["r2"], p1["loglog_r2"]),
        "Logistic regression flags escalations; the share of the response target already used is the "
        "strongest driver (odds ratio %.2f per standard deviation)." % p2["odds_ratio_X3"],
        "Choosing the threshold with money (INR 50 per false alarm, INR 400 per miss) gives %.2f and cuts the "
        "test cost from INR %d to INR %d." % (p2["cost_tau"], p2["cost_test_at_0.5"], p2["cost_test_at_tau"]),
        "Three ticket segments emerge; the escalation rate ranges from %.1f%% to %.1f%%."
        % (100 * io.table("part3_segments.csv")["rows"][0][7], 100 * io.table("part3_segments.csv")["rows"][2][7]),
        "Simple ensembles do not beat logistic regression, so the extra complexity is not justified.",
    ]
    return {
        "title": "Swiggy support decision intelligence",
        "problem": [
            "Swiggy's support team plans staffing on an average resolution time per ticket and wants to "
            "escalate risky tickets to a senior team before they blow up.",
            "Three questions: is the 8 minute planning assumption still right, which tickets will "
            "escalate, and what groups of tickets does the queue contain.",
            "The data is a synthetic table of 800 tickets with seven predictors. Every figure on this "
            "site is read from the project's committed outputs or computed from the same trained model.",
        ],
        "headline": headline, "findings": findings,
    }


@app.get("/api/results/{part}")
def results(part: int):
    if part not in PARTS:
        raise HTTPException(status_code=404, detail="Unknown part %d; use 1 to 4" % part)
    title, res, tables = PARTS[part]
    return {"part": part, "title": title, "metrics": io.results(res),
            "tables": {t.replace(".csv", "").split("_", 1)[1]: io.table(t) for t in tables}}


@app.get("/api/threshold", response_model=ThresholdResponse)
def threshold(tau: float = Query(0.5, ge=0, le=1), cost_fp: float = Query(50, ge=0, le=100000),
              cost_fn: float = Query(400, ge=0, le=100000), dataset: str = Query("test", pattern="^(train|test)$")):
    return service.threshold(tau, dataset, cost_fp, cost_fn)


@app.get("/api/curve")
def curve(cost_fp: float = Query(50, ge=0, le=100000), cost_fn: float = Query(400, ge=0, le=100000),
          dataset: str = Query("test", pattern="^(train|test)$")):
    return service.curve(dataset, cost_fp, cost_fn)


@app.get("/api/knn")
def knn(k: int = Query(5, ge=1, le=41)):
    if k % 2 == 0:
        raise HTTPException(status_code=422, detail="k must be odd so votes cannot tie")
    return service.knn(k)


@app.get("/api/segments")
def segments():
    seg = io.table("part3_segments.csv")
    res = io.results("part3_results.txt")
    return {"profiles": seg, "elbow_k": res["elbow_k"], "hierarchical": io.table("part3_hierarchical.csv"),
            **service.segments_extra()}


@app.get("/api/compare")
def compare(tau: float = Query(0.3, ge=0, le=1), cost_fp: float = Query(50, ge=0, le=100000),
            cost_fn: float = Query(400, ge=0, le=100000)):
    return service.compare(tau, cost_fp, cost_fn)


@app.post("/api/score", response_model=ScoreResponse)
def score(rec: ScoreRequest):
    return service.score(rec)


@app.get("/api/text")
def text():
    s = io.readme_sections()
    keys = ["Part 1 findings", "Part 2 findings", "Part 3 findings", "Part 4 findings",
            "Model-choice memo", "Limitations"]
    return {k: s.get(k, "") for k in keys}


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))


app.mount("/static", StaticFiles(directory=STATIC), name="static")
