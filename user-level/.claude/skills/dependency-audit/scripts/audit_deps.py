#!/usr/bin/env python3
"""Collect dependency facts (vulnerabilities, freshness, license) from free public APIs.

Usage:
    python audit_deps.py [project_dir] [--packages extra.json] [--direct-only]

Reads requirements*.txt (PyPI) and package.json / package-lock.json (npm) found in
project_dir. For other ecosystems pass --packages, a JSON list like
    [{"ecosystem": "Go", "name": "github.com/x/y", "version": "1.2.3"}]
(ecosystem names are OSV's: PyPI, npm, Go, crates.io, Maven, NuGet, RubyGems, Packagist).

Prints one JSON document on stdout; progress and warnings go to stderr.
Standard library only, so nothing has to be installed.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

OSV_BATCH = "https://api.osv.dev/v1/querybatch"
OSV_VULN = "https://api.osv.dev/v1/vulns/{}"
PYPI = "https://pypi.org/pypi/{}/json"
NPM = "https://registry.npmjs.org/{}"
TIMEOUT = 20
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "env", "dist", "build", "__pycache__"}


def log(message):
    print(message, file=sys.stderr)


def http_json(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"User-Agent": "dependency-audit-skill", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        log(f"warning: {url} failed: {error}")
        return None


def find_files(root, pattern):
    return [p for p in root.rglob(pattern) if not SKIP_DIRS & set(p.parts)]


# ---------------------------------------------------------------- parsing

def parse_requirements(path):
    packages = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#")[0].strip()
        if not line or line.startswith(("-", "git+", "http")):
            continue
        match = re.match(r"^([A-Za-z0-9._-]+)(\[[^\]]*\])?\s*(.*)$", line)
        if not match:
            continue
        name, spec = match.group(1), match.group(3).split(";")[0].strip()
        pinned = re.match(r"^===?\s*([^\s,]+)$", spec)
        packages.append({"ecosystem": "PyPI", "name": name, "version": pinned.group(1) if pinned else None,
                         "spec": spec or "(any)", "direct": True, "source": str(path)})
    return packages


def parse_npm(package_json, direct_only):
    manifest = json.loads(package_json.read_text(encoding="utf-8"))
    direct = {}
    for key in ("dependencies", "devDependencies", "optionalDependencies"):
        direct.update(manifest.get(key, {}))
    lock = package_json.with_name("package-lock.json")
    packages = []
    if lock.exists():
        locked = json.loads(lock.read_text(encoding="utf-8")).get("packages", {})
        for key, info in locked.items():
            if not key or "version" not in info:
                continue
            name = key.split("node_modules/")[-1]
            is_direct = key == f"node_modules/{name}" and name in direct
            if direct_only and not is_direct:
                continue
            packages.append({"ecosystem": "npm", "name": name, "version": info["version"], "direct": is_direct,
                             "dev": info.get("dev", False), "source": str(lock)})
    else:
        for name, spec in direct.items():
            exact = re.match(r"^\d+\.\d+\.\d+$", spec)
            packages.append({"ecosystem": "npm", "name": name, "version": spec if exact else None,
                             "spec": spec, "direct": True, "source": str(package_json)})
    return packages


# ---------------------------------------------------------------- enrichment

def fixed_versions(vuln):
    fixed = set()
    for affected in vuln.get("affected", []):
        for rng in affected.get("ranges", []):
            for event in rng.get("events", []):
                if "fixed" in event:
                    fixed.add(event["fixed"])
    return sorted(fixed)


def summarize_vuln(vuln):
    severity = (vuln.get("database_specific") or {}).get("severity")
    cvss = [s.get("score") for s in vuln.get("severity", [])]
    cves = [a for a in vuln.get("aliases", []) if a.startswith("CVE-")]
    return {"id": vuln["id"], "cves": cves, "severity": severity or "UNKNOWN", "cvss_vectors": cvss,
            "summary": vuln.get("summary", ""), "fixed_in": fixed_versions(vuln)}


def query_vulnerabilities(packages):
    queryable = [p for p in packages if p["version"]]
    for start in range(0, len(queryable), 500):
        chunk = queryable[start:start + 500]
        result = http_json(OSV_BATCH, {"queries": [
            {"package": {"name": p["name"], "ecosystem": p["ecosystem"]}, "version": p["version"]} for p in chunk]})
        if result is None:
            for p in chunk:
                p["vulnerabilities_error"] = True
            continue
        for p, entry in zip(chunk, result.get("results", [])):
            p["_vuln_ids"] = [v["id"] for v in entry.get("vulns", [])]
    ids = sorted({i for p in packages for i in p.get("_vuln_ids", [])})
    with ThreadPoolExecutor(8) as pool:
        details = dict(zip(ids, pool.map(lambda i: http_json(OSV_VULN.format(i)), ids)))
    for p in packages:
        p["vulnerabilities"] = [summarize_vuln(details[i]) if details.get(i) else {"id": i} for i in p.pop("_vuln_ids", [])]


def enrich_pypi(p):
    data = http_json(PYPI.format(p["name"]))
    if not data:
        return
    info = data["info"]
    p["latest"] = info["version"]
    p["license"] = info.get("license_expression") or (info.get("license") or "")[:120] or None
    p["license_classifiers"] = [c.split("::")[-1].strip() for c in info.get("classifiers", []) if c.startswith("License ::")]
    p["deprecated"] = bool(data.get("info", {}).get("yanked"))
    if p["version"]:
        files = data.get("releases", {}).get(p["version"], [])
        p["yanked"] = any(f.get("yanked") for f in files)
        p["released"] = min((f["upload_time_iso_8601"] for f in files), default=None)
    latest_files = data.get("urls", [])
    p["latest_released"] = min((f["upload_time_iso_8601"] for f in latest_files), default=None)


def enrich_npm(p):
    name = p["name"].replace("/", "%2F")
    latest = http_json(f"{NPM.format(name)}/latest")
    if latest:
        p["latest"] = latest.get("version")
        p["license"] = latest.get("license") if isinstance(latest.get("license"), str) else json.dumps(latest.get("license"))
        if latest.get("deprecated"):
            p["deprecated"] = latest["deprecated"]
    if p["version"] and p["version"] != p.get("latest"):
        current = http_json(f"{NPM.format(name)}/{p['version']}")
        if current:
            p["license"] = p.get("license") or current.get("license")
            if current.get("deprecated"):
                p["deprecated"] = current["deprecated"]


def classify_gap(p):
    """Major/minor/patch distance between installed and latest, when both parse."""
    def parts(version):
        numbers = re.findall(r"\d+", version or "")
        return [int(n) for n in numbers[:3]] + [0] * (3 - len(numbers[:3]))
    if not p.get("version") or not p.get("latest"):
        return None
    current, latest = parts(p["version"]), parts(p["latest"])
    if current >= latest:
        return "up-to-date"
    return ("major", "minor", "patch")[next(i for i in range(3) if current[i] != latest[i])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--packages", help="JSON file with extra packages for other ecosystems")
    parser.add_argument("--direct-only", action="store_true", help="ignore transitive npm packages from the lockfile")
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    packages = []
    for path in find_files(root, "requirements*.txt"):
        packages += parse_requirements(path)
    for path in find_files(root, "package.json"):
        packages += parse_npm(path, args.direct_only)
    if args.packages:
        for item in json.loads(Path(args.packages).read_text(encoding="utf-8")):
            packages.append({"direct": True, "source": args.packages, **item})
    if not packages:
        log("No supported manifest found; pass --packages for other ecosystems.")

    # Deduplicate on (ecosystem, name, version), keeping the "direct" flag if any entry has it.
    unique = {}
    for p in packages:
        key = (p["ecosystem"], p["name"].lower(), p.get("version"))
        if key in unique:
            unique[key]["direct"] = unique[key]["direct"] or p["direct"]
        else:
            unique[key] = p
    packages = list(unique.values())
    log(f"{len(packages)} packages to analyse")

    query_vulnerabilities(packages)
    with ThreadPoolExecutor(8) as pool:
        list(pool.map(lambda p: enrich_pypi(p) if p["ecosystem"] == "PyPI" else enrich_npm(p) if p["ecosystem"] == "npm" else None, packages))
    for p in packages:
        p["version_gap"] = classify_gap(p)

    print(json.dumps({"generated": datetime.now(timezone.utc).isoformat(), "project": str(root), "packages": packages}, indent=2))


if __name__ == "__main__":
    main()
