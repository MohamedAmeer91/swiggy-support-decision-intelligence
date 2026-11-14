# Progress Log: four capstone projects

Folder: `E:\IIT\Capestone_Project\OtherProjects`. This file sits outside the four repos, so it is not pushed anywhere.

Lifecycle used for every project: Plan, Design, Implement, Test, Deploy. Work started on 14 Nov 2026. The brief window closes on 16 Nov 2026. The exact closing time on the course platform is still unknown.

## Final state

| Project | Local folder | GitHub repo | Tests (local, git-ignored) | Generator hash starts |
|---|---|---|---|---|
| Apna Recruitment | `apna-recruitment` | MohamedAmeer91/apna-recruitment-decision-intelligence | 37 pass | `0537bc7f` |
| Flipkart E-commerce | `flipkart-ecommerce` | MohamedAmeer91/flipkart-ecommerce-decision-intelligence | 14 pass | `c6f249ba` |
| PhonePe Banking | `phonepe-banking` | MohamedAmeer91/phonepe-banking-decision-intelligence | 25 pass | `e85e7605` |
| Swiggy Support | `swiggy-support` | MohamedAmeer91/swiggy-support-decision-intelligence | 13 pass | `7cb48ef8` |

All four repos are pushed to `origin/main` (the graded submission, unchanged since the first push) and `origin/dev` (the web layer). The Apna, Flipkart and PhonePe repos had 13 commits on `main` and Swiggy had 14, counted before the last history rewrite.

## Timeline of changes

### 1. Setup
- Found four requirement briefs, one per project, in the root folder.
- Created one folder per project and moved each brief to `docs/REQUIREMENTS.md`.
- Ran `git init -b main` in each folder and added a `.gitignore` (`__pycache__/`, `*.pyc`, `.venv/`, `.ipynb_checkpoints/`, `.env`).
- Made an initial commit in each repo.

### 2. Plan phase
- Four parallel planning agents wrote `docs/PLAN.md` for each project.
- Each plan covers the brief summary, a task-to-marks map, constraints, assumptions, risks, milestones with exit criteria, the tech stack and the data needed.
- Each plan was committed locally as "Add project plan".
- All four plans raised the same open questions: submission closing time, GitHub details, NumPy version, and line endings.

### 3. Environment
- Checked installed Pythons. Found Anaconda 3.13 and python.org 3.10.11, and the `python` command on PATH only opened the Microsoft Store shortcut.
- Chose Python 3.10.11.
- Created a `.venv` in each project and installed `numpy==1.26.4` in each.
- Added `.gitattributes` forcing LF line endings, to keep data hashes stable.
- Committed `.gitattributes` in each repo.
- Suggested repo names and descriptions.

### 4. Design phase, Apna first
- An agent wrote Apna's `docs/DESIGN.md` and committed it.
- It covered the layout, generator, modules, per-Part algorithms and outputs, memo, README outline, test strategy and deploy checklist.
- Open decisions were approved:
  - mark `data/records.csv` as `-text`,
  - pin NumPy 1.26.4,
  - ask the user if `elbow_k` is undefined,
  - memo default is logistic.

### 5. Implement phase
- **Apna:** generator verbatim, data, `requirements.txt`, `common.py`, `part1.py` to `part4.py`, all 12 outputs, README. Committed after each step.
  - Checkpoints matched. `elbow_k` was valid at 3.
  - The memo recommends logistic at threshold 0.15, costing INR 6,050 on the test rows.
- **Flipkart, PhonePe, Swiggy:** one agent each ran design, implement, test and deploy autonomously.
  - Each wrote its own `docs/DESIGN.md` and `docs/DECISIONS.md`, built the generator, parts and README, and wrote tests.
  - Checkpoints matched in all three.

### 6. Test phase
- Apna: a separate agent wrote 37 tests and fixed its own over-strict tests. No code defects were found.
- Flipkart, PhonePe and Swiggy tests were written by their agents (14, 25 and 13 tests).
- Tests cover keys, headers, row counts, formats, invariants, forbidden-routine and link grep, README order and numbers, and determinism.

### 7. Deploy phase (local)
- Clean-clone runs in a fresh venv matched the committed outputs byte for byte in all four projects.
- Temp clones were deleted.
- Each repo has one branch (`main`) and a clean working tree.

### 8. Cleanup decisions
- `data/records.csv` and `generate_data.py` are marked `-text`, because the CSV hash depends on CRLF endings and the earlier LF rule would have broken it.
- Removed `https://` prefixes from `docs/` text in all four repos, because the brief says extra links are not graded.
- Untracked `tests/` and git-ignored it. Tests stay on disk locally.
- Kept `docs/` tracked.

### 9. History cleanup (before any push)
- Dropped `tests/` from the whole history of all four repos.
- Rewrote commit authors to the GitHub no-reply identity `MohamedAmeer91@users.noreply.github.com`.
- Verified: no `tests/` paths remain in history.

### 10. Remotes and push
- Added `origin` to each repo (the PhonePe URL was corrected after a typo in the first message).
- Ran `git push -u origin main` in all four repos. Each created a new `main` branch and set up tracking.
- Did not force-push.

### 11. `dev` branch
- Created a local `dev` branch in each repo at the same commit as `main`. It was pushed later, together with the web work.

### 12. Web layer (on `dev`, in `web/`)
One agent per project ran plan, design, implement, test and deploy. Each app is a FastAPI backend (pydantic validation, JSON errors) plus a plain HTML/CSS/ES-module frontend with inline-SVG charts, no build step and light/dark themes. It only reads `outputs/` and imports from the graded `common.py` (plus `part3.py` for PhonePe's K-means). The graded code, data, outputs, root README and root `requirements.txt` were not changed. Web dependencies are in `web/requirements.txt`.

| Project | Pages | Interactive pieces | Web tests |
|---|---|---|---|
| Apna | Overview, Parts 1-4, record scorer, memo, limitations | Threshold slider (confusion matrix, ROC, INR cost), KNN selector, segment explorer, ensemble lab, scorer | 14 |
| Flipkart | Overview, Parts 1-4, memo, limitations | Same set, with an editable cost rule | 15 |
| PhonePe | Overview, Parts 1-4, memo, limitations | Same set, plus a borrower scorer, segment assignment, AdaBoost round viewer | 22 |
| Swiggy | Overview, Parts 1-4, Score a ticket, memo and limits | Same set, plus per-feature contributions in the scorer | 18 |

- Tests cross-check API numbers against the `outputs/` files, validation errors (422 and 404) and static files.
- Re-running `generate_data.py` and `part1.py` to `part4.py` still reproduced the outputs, with git clean.
- `git diff main` showed only `web/` additions (plus `.gitignore`).
- `web/.gitignore` re-includes `web/tests/`, because the root `.gitignore` ignores `tests/`.

### 13. Docker
- Each agent wrote `web/Dockerfile` (`python:3.10-slim`, installs `web/requirements.txt`, copies the files the app needs, serves on port 8000).
- Added `.dockerignore` on `dev` (excludes `.venv`, `.git`, caches, tests, `docs/`).
- Built all four images (`cap-<project>:dev`) and ran each container. Every GET endpoint and linked static file returned 200 (Apna 16, Flipkart 15, PhonePe 11, Swiggy 12 paths). Every POST endpoint returned 200 for a valid body and 422 for an empty one. No Dockerfile fixes were needed.
- Test containers were removed. The user deleted the Apna image afterwards and can rebuild it with `docker build -f web/Dockerfile -t cap-apna-recruitment:dev .` from the repo folder.

### 14. Push of `dev`
- Pushed only `dev` with `git push -u origin dev`, then pushed the `.dockerignore` commits. `main` was not pushed again.
- Verified: `main` equals `origin/main` in all four repos, `dev` has 6, 6, 4 and 6 commits not on `main` (Apna, Flipkart, PhonePe, Swiggy), nothing is unpushed, and `main` contains no `web/` files.

## Preferences recorded
- Work only inside this folder.
- Do not push to `main` after the submission push. Web work goes to `dev` only.

## Still to do (by the user)
- Open each web app in a browser and try the sliders, charts and forms. Only JavaScript syntax checks and HTTP-level tests were done, not a visual check.
- Confirm each GitHub repo is **public**, has `main` as the default branch, and shows the README and files.
- The briefs want `main` as the only branch. Delete `dev` on GitHub before submitting if that matters (`git push origin --delete dev`).
- Check that only the user's account is listed as a contributor.
- Submit each repo link on the course platform before the closing time on 16 Nov 2026.
- Optional: send a personal email if GitHub should link commits to the user's profile, and rewrite authors again if so.

## Known notes
- `docs/` still describes the tests, which are no longer in the repos, by the user's choice.
- Memos cost only the logistic model and say the other models' costs were not computed. I did not check the Flipkart memo myself.
- The Apna agent first reported its own count as 37 tests. Other counts come from agent reports and I did not rerun them after the history rewrites.
