#!/usr/bin/env python3
"""
Citation linter for substratum.

Walks every JSON file under data/ and benchmarks/, extracts arXiv IDs from both
structured `arxiv` fields and free-form citation strings, then queries the
arXiv API (https://arxiv.org/help/api) to verify:

  1. The ID resolves to a real paper.
  2. The first author's surname (or the first surname appearing in the
     citation string) matches the surname of the arXiv author list.

Mismatch cases this is designed to catch:
  - typoed arXiv IDs (e.g. 2202.04077 standing in for 1907.11594);
  - structured `arxiv` fields glued to the wrong citation by copy-paste;
  - papers that have been withdrawn or replaced with unrelated content.

Usage:
    python3 scripts/check_citations.py            # check everything
    python3 scripts/check_citations.py file ...   # check specific files
    python3 scripts/check_citations.py --offline  # parse-only, no network

arXiv's published rate limit is 1 request per 3 seconds. We batch up to 100
IDs per request via the `id_list` parameter, so the full catalogue resolves
in a handful of calls. Results are cached in .arxiv_cache.json so reruns
are nearly free.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from glob import glob
from pathlib import Path

ARXIV_RE = re.compile(
    r"(?:arXiv:|arxiv:|arxiv\.org/abs/)\s*"
    r"([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})",
    re.IGNORECASE,
)

ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}
API_URL = "https://export.arxiv.org/api/query?id_list={}&max_results={}"
CACHE_PATH = Path(".arxiv_cache.json")
RATE_LIMIT_SECONDS = 3.5  # arXiv API courtesy: ~1 request per 3 seconds
BATCH_SIZE = 50


def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def collect_citations(obj):
    """
    Return list of (arxiv_id, citation_text, json_path).

    A citation is identified by either a structured `.arxiv` field (in which
    case the sibling `.citation` field, if any, is the citation text) or by
    an arXiv ID embedded in any other string field.
    """
    out = []

    def descend(node, path):
        if isinstance(node, dict):
            if "arxiv" in node and isinstance(node["arxiv"], str):
                aid = node["arxiv"].strip()
                cite = node.get("citation") or node.get("reference") or ""
                if not cite:
                    # Find any sibling text-y field
                    for k in ("note", "label", "summary"):
                        if k in node and isinstance(node[k], str):
                            cite = node[k]
                            break
                out.append((aid, cite, path))
            for k, v in node.items():
                descend(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                descend(v, f"{path}[{i}]")
        elif isinstance(node, str):
            for m in ARXIV_RE.finditer(node):
                out.append((m.group(1), node, path))

    descend(obj, "")
    return out


def load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))


_last_request_time = 0.0


def _parse_entry(entry):
    title_el = entry.find("a:title", ATOM_NS)
    published_el = entry.find("a:published", ATOM_NS)
    id_el = entry.find("a:id", ATOM_NS)
    authors = [
        (a.find("a:name", ATOM_NS).text or "").strip()
        for a in entry.findall("a:author", ATOM_NS)
    ]
    title = (title_el.text or "").strip() if title_el is not None else ""
    year = ""
    if published_el is not None and published_el.text:
        year = published_el.text[:4]
    aid = ""
    if id_el is not None and id_el.text:
        # http://arxiv.org/abs/2308.06230v3 → 2308.06230
        m = re.search(r"abs/([^/]+?)(?:v\d+)?$", id_el.text.strip())
        if m:
            aid = m.group(1)
    return aid, {"title": title, "authors": authors, "year": year}


def fetch_arxiv_batch(arxiv_ids, cache):
    """
    Resolve a list of arxiv IDs, populating cache. Uses a single API call per
    BATCH_SIZE-sized chunk and respects the courtesy rate limit between calls.
    """
    global _last_request_time
    pending = [aid for aid in arxiv_ids if aid not in cache]
    pending = list(dict.fromkeys(pending))  # de-duplicate, preserve order

    for start in range(0, len(pending), BATCH_SIZE):
        chunk = pending[start : start + BATCH_SIZE]
        elapsed = time.time() - _last_request_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        _last_request_time = time.time()

        url = API_URL.format(",".join(chunk), len(chunk))
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "substratum-citation-checker/0.1 "
                    "(+https://github.com/dritory/substratum)"
                )
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
        except Exception as exc:
            for aid in chunk:
                cache[aid] = {"error": f"fetch_failed: {exc}"}
            continue

        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            for aid in chunk:
                cache[aid] = {"error": f"parse_failed: {exc}"}
            continue

        # arXiv returns one <entry> per ID. Map by parsed ID; any chunk member
        # with no entry (or an "Error" entry) gets an explicit failure record.
        seen = {}
        for entry in root.findall("a:entry", ATOM_NS):
            aid, meta = _parse_entry(entry)
            if not aid:
                continue
            if meta["title"].lower().startswith("error"):
                seen[aid] = {"error": "arxiv_returned_error_entry"}
            else:
                seen[aid] = meta
        for aid in chunk:
            cache[aid] = seen.get(aid, {"error": "id_not_in_response"})


def fetch_arxiv(arxiv_id, cache):
    if arxiv_id not in cache:
        fetch_arxiv_batch([arxiv_id], cache)
    return cache[arxiv_id]


def surname(name):
    """
    Best-effort author-surname extraction from arXiv 'Firstname M. Lastname'
    or 'Lastname, Firstname' forms.
    """
    name = name.strip()
    if "," in name:
        return name.split(",", 1)[0].strip().lower()
    parts = name.split()
    return parts[-1].strip().lower() if parts else ""


def normalize(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def collaboration_token(name):
    """
    For author names like 'Planck Collaboration', 'ATLAS Collaboration',
    'et al. (DES Collaboration)', return the experiment token ('planck',
    'atlas', 'des'). Returns None if the name does not look like a
    collaboration form.
    """
    n = name.lower()
    if "collaboration" not in n:
        return None
    # Strip 'et al.', '(', ')', and 'collaboration'
    cleaned = re.sub(r"\bet al\.?\b|\(|\)|\bcollaboration\b", " ", n)
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned).strip()
    if not cleaned:
        return None
    # First token is the experiment name
    return cleaned.split()[0]


def author_in_citation(arxiv_authors, citation_text):
    """
    Best-effort match: try collaboration tokens first ('planck', 'atlas',
    'desi'), then individual surnames of the first few authors. Returns the
    matched token, or None if nothing matched.
    """
    cite_tokens = set(normalize(citation_text).split())
    cite_norm = normalize(citation_text)

    # Collaboration tokens (most reliable for big-experiment papers).
    for author in arxiv_authors[:5]:
        tok = collaboration_token(author)
        if tok and tok in cite_tokens:
            return tok

    # Individual surnames.
    for author in arxiv_authors[:5]:
        if "collaboration" in author.lower():
            continue
        sn = surname(author)
        if not sn:
            continue
        if sn in cite_tokens:
            return sn
        # Compound surnames: 'de blas', 'di valentino'.
        if len(sn) > 3 and sn in cite_norm:
            return sn

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Specific JSON files (default: all)")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip network; only verify JSON parseability and report counts.",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Only print failures and summary."
    )
    args = parser.parse_args()

    if args.files:
        files = sorted(args.files)
    else:
        files = sorted(
            glob("data/*.json")
            + glob("benchmarks/*.json")
            + glob("puzzles/*.json")
            + glob("mechanisms/*.json")
            + glob("frameworks/*.json")
        )

    cache = load_cache() if not args.offline else {}
    failures = []
    n_checked = 0

    # First pass: parse files, collect every (file, citation, id) triple, and
    # build a flat ID list to resolve in batches.
    per_file = []
    all_ids = []
    for f in files:
        try:
            obj = json.loads(Path(f).read_text())
        except json.JSONDecodeError as exc:
            failures.append((f, "*", "*", f"json_parse_error: {exc}"))
            per_file.append((f, []))
            continue
        cites = collect_citations(obj)
        per_file.append((f, cites))
        all_ids.extend(aid for aid, _, _ in cites)
        if not args.quiet:
            print(f"{f}: {len(cites)} arxiv references")

    if args.offline:
        print(f"\n[offline] {sum(len(c) for _, c in per_file)} citations parsed.")
        return

    # Resolve every uncached ID in batches.
    fetch_arxiv_batch(all_ids, cache)
    save_cache(cache)

    for f, cites in per_file:
        for aid, cite_text, path in cites:
            meta = cache.get(aid, {"error": "missing_from_cache"})
            n_checked += 1
            if "error" in meta:
                failures.append((f, aid, path, meta["error"]))
                continue
            matched = author_in_citation(meta.get("authors", []), cite_text)
            if matched is None:
                expected_surname = (
                    surname(meta["authors"][0]) if meta.get("authors") else "<unknown>"
                )
                failures.append(
                    (
                        f,
                        aid,
                        path,
                        f"author_mismatch: arxiv first author '{expected_surname}' "
                        f"not found in citation text. arxiv title: {meta.get('title', '')[:80]!r}",
                    )
                )

    print()
    print(f"Checked {n_checked} arXiv references across {len(files)} files.")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f, aid, path, msg in failures:
            print(f"  {f} :: {path} [arxiv:{aid}]")
            print(f"      {msg}")
        sys.exit(1)
    print("All citations look consistent.")


if __name__ == "__main__":
    main()
