# Deploy guide: web layer of the four capstone projects

This covers running the interactive web apps locally, with or without Docker. The apps live in `web/` on the `dev` branch of each repo. `main` has no web layer. This file sits in the parent folder, outside the repos, so it is not pushed.

Nothing is hosted online. "Deploy" here means running each app on this machine.

## Apps and ports

| Project | Folder | Image name | Container name | Host port |
|---|---|---|---|---|
| Apna Recruitment | `apna-recruitment` | `cap-apna-recruitment:dev` | `apna` | 8001 |
| Flipkart E-commerce | `flipkart-ecommerce` | `cap-flipkart-ecommerce:dev` | `flipkart` | 8002 |
| PhonePe Banking | `phonepe-banking` | `cap-phonepe-banking:dev` | `phonepe` | 8003 |
| Swiggy Support | `swiggy-support` | `cap-swiggy-support:dev` | `swiggy` | 8004 |

Each app listens on port 8000 inside its container. The host port is the left-hand number in `-p`. Open `127.0.0.1:<host port>` in a browser.

## Prerequisites
- Docker Desktop is running. Check with `docker info`. If it fails with an error about `dockerDesktopLinuxEngine`, the engine is not started yet.
- Git has the `dev` branch checked out in the repo you are building. `main` has no `web/` folder.

## 1. Build the images

Run from inside each repo folder. The build context must be the repo root (the trailing `.`), and the Dockerfile is at `web/Dockerfile`, so `-f` is needed. A plain `docker build -t name .` will fail because there is no root-level Dockerfile.

```
cd E:\IIT\Capestone_Project\OtherProjects\apna-recruitment
git checkout dev
docker build -f web/Dockerfile -t cap-apna-recruitment:dev .

cd E:\IIT\Capestone_Project\OtherProjects\flipkart-ecommerce
git checkout dev
docker build -f web/Dockerfile -t cap-flipkart-ecommerce:dev .

cd E:\IIT\Capestone_Project\OtherProjects\phonepe-banking
git checkout dev
docker build -f web/Dockerfile -t cap-phonepe-banking:dev .

cd E:\IIT\Capestone_Project\OtherProjects\swiggy-support
git checkout dev
docker build -f web/Dockerfile -t cap-swiggy-support:dev .
```

Rebuild only after changing code on `dev`. A `.dockerignore` in each repo keeps `.venv`, `.git`, caches, tests and `docs/` out of the build.

What each image contains (`python:3.10-slim` base, installs `web/requirements.txt`):
- Apna: `common.py`, `data/`, `outputs/`, `web/`.
- Flipkart: the same, plus `README.md`.
- PhonePe: `common.py`, `part3.py` (its app imports it), `README.md`, `data/`, `outputs/`, `web/`.
- Swiggy: `requirements.txt`, `common.py`, `README.md`, `data/`, `outputs/`, `web/`.

## 2. Run all four at once

```
docker run -d --rm --name apna     -p 8001:8000 cap-apna-recruitment:dev
docker run -d --rm --name flipkart -p 8002:8000 cap-flipkart-ecommerce:dev
docker run -d --rm --name phonepe  -p 8003:8000 cap-phonepe-banking:dev
docker run -d --rm --name swiggy   -p 8004:8000 cap-swiggy-support:dev
```

Open:
- Apna: `127.0.0.1:8001`
- Flipkart: `127.0.0.1:8002`
- PhonePe: `127.0.0.1:8003`
- Swiggy: `127.0.0.1:8004`

Flags: `-d` runs in the background, `--rm` deletes the container when it stops (the image stays), `--name` gives it a short name.

## 3. Run one app in the foreground

```
docker run --rm -p 8000:8000 cap-apna-recruitment:dev
docker run --rm -p 8000:8000 cap-flipkart-ecommerce:dev
docker run --rm -p 8000:8000 cap-phonepe-banking:dev
docker run --rm -p 8000:8000 cap-swiggy-support:dev
```

Open `127.0.0.1:8000`. Press Ctrl+C to stop. Run only one of these at a time, since they share port 8000.

## 4. Check, stop and clean up

```
docker ps                                   # running containers
docker ps -a                                # all containers
docker logs apna                            # logs of one container
docker stop apna flipkart phonepe swiggy    # stop all four (--rm removes them)
docker images "cap-*"                       # list the capstone images
docker rmi cap-apna-recruitment:dev         # remove an image (stop its container first)
```

## 5. Run without Docker

From inside a repo folder on the `dev` branch, using that project's own virtual environment (Python 3.10, NumPy 1.26.4):

```
.venv\Scripts\python.exe -m pip install -r web/requirements.txt
.venv\Scripts\python.exe -m uvicorn web.app:app --port 8000
```

Web tests:

```
.venv\Scripts\python.exe -m unittest discover -s web/tests -t .
```

## 6. What was verified

- All four images built without errors.
- All four containers started. Every GET endpoint in each app's API schema and every linked JS and CSS file returned 200 (Apna 16, Flipkart 15, PhonePe 11, Swiggy 12 paths).
- Every POST endpoint returned 200 for a valid body and 422 for an empty body. These are `/api/score` in all four apps, plus `/api/segment/assign` and `/api/ensemble` in PhonePe.
- No Dockerfile changes were needed.
- Not verified: the pages have not been looked at in a browser, so the sliders, charts and forms are unchecked visually. Only JavaScript syntax checks and HTTP-level requests were done.

## 7. Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `docker build` says it cannot read the Dockerfile | Missing `-f web/Dockerfile`, or you are not in the repo root. |
| `docker build` says `web/` is not found | `main` is checked out. Run `git checkout dev`. |
| Error mentioning `dockerDesktopLinuxEngine` | Docker Desktop is not running. Start it and wait for the engine. |
| `port is already allocated` | Another container or program uses that host port. Stop it or pick another left-hand port. |
| Container exits straight away | Run without `-d` or use `docker logs <name>` to see the error. |
| Page loads but the data looks old | The image was built before the outputs changed. Rebuild it. |

## 8. Branch and push rules
- `main` is the graded submission and stays unchanged. Do not push to it.
- The web layer and Docker files live on `dev` only. Push with `git push origin dev`.
- The briefs want `main` as the only branch. If that matters, delete `dev` on GitHub before submitting: `git push origin --delete dev`.
