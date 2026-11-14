"""Read-only parsers for outputs/*.txt, outputs/*.csv and README sections."""
import csv
import os
import re
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "outputs")
README = os.path.join(ROOT, "README.md")

_lock = threading.Lock()
_cache = {}


def _num(s):
    s = s.strip()
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def _cached(path, parse):
    mtime = os.path.getmtime(path)
    with _lock:
        hit = _cache.get(path)
        if hit and hit[0] == mtime:
            return hit[1]
    value = parse(path)
    with _lock:
        _cache[path] = (mtime, value)
    return value


def _parse_results(path):
    out = {}
    with open(path, newline="") as f:
        for line in f:
            if " = " in line:
                k, v = line.rstrip("\n").split(" = ", 1)
                out[k.strip()] = _num(v)
    return out


def _parse_csv(path):
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    return {"header": rows[0], "rows": [[_num(c) for c in r] for r in rows[1:]]}


def results(name):
    """Key/value metrics of outputs/<name> (e.g. part2_results.txt)."""
    return _cached(os.path.join(OUT_DIR, name), _parse_results)


def table(name):
    """Header and rows of outputs/<name> (a CSV file)."""
    return _cached(os.path.join(OUT_DIR, name), _parse_csv)


def _parse_readme(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    sections = {}
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        title, _, body = chunk.partition("\n")
        sections[title.strip()] = body.strip()
    return sections


def readme_sections():
    return _cached(README, _parse_readme)
