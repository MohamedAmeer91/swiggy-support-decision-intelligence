# Interactive portfolio layer

A FastAPI backend and plain HTML/CSS/JavaScript frontend over the Swiggy support project. It only
reads `outputs/` and imports `common.py`; the graded files are never changed. No network is needed at run time.

## Run locally (Windows PowerShell, from the repository root)

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r web/requirements.txt
.venv\Scripts\python.exe -m uvicorn web.app:app --port 8000
```

On macOS or Linux use `.venv/bin/python` instead. Then open localhost port 8000 in a browser
(address `127.0.0.1:8000`). Interactive API docs are at `/docs`.

## Tests

```
.venv\Scripts\python.exe -m unittest discover -s web/tests -t .
```

## Docker

Build from the repository root so the data, outputs and helper code are included:

```
docker build -f web/Dockerfile -t swiggy-support-web .
docker run --rm -p 8000:8000 swiggy-support-web
```

## What is interactive
- Part 2: threshold slider with live confusion matrix, precision, recall, F1, ROC style curve and INR cost; editable costs; KNN K selector.
- Part 3: segment and outcome filters on the PCA scatter.
- Part 4: threshold control for the model comparison and voting table.
- Score a ticket: seven inputs to escalation probability and per-feature contribution.

Design notes are in `docs/` (PLAN, DESIGN, DECISIONS).
