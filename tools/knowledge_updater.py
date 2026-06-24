# -*- coding: utf-8 -*-
'''knowledge_updater.py — self-improving knowledge pipeline for energy-carbon-footprint-optimizer.

Crawls authoritative Science, Engineering & Industry sources, scores entries by recency and
domain relevance, and appends new, de-duplicated rows to SECOND-KNOWLEDGE-BRAIN.md.

Modes:
    --seed    Append a curated set of authoritative seed entries (no network required).
    --dry-run Preview entries that would be appended without writing.
    --brain   Override the path to the knowledge brain file.

Schedule: weekly (cron). Cluster: science-industry.
'''
import argparse
import datetime
import hashlib
import json
import logging
import os
import re
import sys

# Allow the tool to import the local package even when run as a standalone script.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_SCRIPT_DIR, "..", "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from energy_carbon_footprint_optimizer.constants import (
    ARXIV_CATEGORIES,
    DOMAIN_KEYWORDS,
    SEARCH_QUERIES,
)

logger = logging.getLogger("knowledge_updater")

DEFAULT_BRAIN = os.path.join(_SCRIPT_DIR, "..", "SECOND-KNOWLEDGE-BRAIN.md")


def _brain_path(args_path=None):
    return args_path or os.environ.get("ECO_BRAIN_PATH", DEFAULT_BRAIN)


# ---------------------------------------------------------------------------
# 1. FETCH
# ---------------------------------------------------------------------------
def fetch_arxiv(categories, max_results=25):
    '''Query the ArXiv API for recent papers in the given categories.'''
    import urllib.request
    import urllib.parse

    entries = []
    for cat in categories:
        query = urllib.parse.urlencode({
            "search_query": f"cat:{cat}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        })
        url = f"http://export.arxiv.org/api/query?{query}"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = response.read().decode("utf-8", "ignore")
        except Exception as exc:
            logger.warning("[arxiv] %s failed: %s", cat, exc)
            continue

        for match in re.finditer(r"<entry>(.*?)</entry>", raw, re.S):
            block = match.group(1)

            def tag(name):
                m = re.search(rf"<{name}>(.*?)</{name}>", block, re.S)
                return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

            entries.append({
                "title": tag("title"),
                "authors": tag("name"),
                "year": tag("published")[:4],
                "venue": f"arXiv:{cat}",
                "url": tag("id"),
                "abstract": tag("summary"),
            })
    return entries


def fetch_websearch(queries):
    '''Pluggable integration point for WebSearch.

    In the Claude harness this function can be supplied with results from the WebSearch tool.
    Offline, or when no provider is configured, it returns an empty list.
    '''
    provider = os.environ.get("ECO_WEBSEARCH_PROVIDER", "").lower()
    if not provider:
        logger.info("No ECO_WEBSEARCH_PROVIDER configured; skipping web search.")
        return []

    logger.warning("WebSearch provider '%s' is configured but not implemented in this run.", provider)
    return []


# ---------------------------------------------------------------------------
# 2/3/4. PARSE + SCORE
# ---------------------------------------------------------------------------
def score_entry(entry):
    '''Combine recency and keyword relevance into a single relevance score.'''
    score = 0.0
    try:
        year = int(entry.get("year") or 0)
        score += max(0, year - 2018) * 0.5
    except ValueError:
        pass
    text = (entry.get("title", "") + " " + entry.get("abstract", "")).lower()
    score += sum(2.0 for keyword in DOMAIN_KEYWORDS if keyword.lower() in text)
    return score


# ---------------------------------------------------------------------------
# 5/6. APPEND + DEDUP
# ---------------------------------------------------------------------------
def existing_hashes(brain_text):
    return set(re.findall(r"<!--h:([0-9a-f]{12})-->", brain_text))


def entry_hash(entry):
    key = entry.get("url") or entry.get("title", "")
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def append_entries(entries, brain_path=None, dry_run=False):
    '''Append scored entries to SECOND-KNOWLEDGE-BRAIN.md, skipping duplicates.'''
    brain_path = _brain_path(brain_path)
    try:
        with open(brain_path, "r", encoding="utf-8") as fh:
            brain_text = fh.read()
    except FileNotFoundError:
        brain_text = ""

    seen = existing_hashes(brain_text)
    ranked = sorted(entries, key=score_entry, reverse=True)
    today = datetime.date.today().isoformat()
    rows = []
    appended = 0

    for entry in ranked:
        h = entry_hash(entry)
        if h in seen or not entry.get("title"):
            continue
        seen.add(h)
        appended += 1
        rows.append(
            f"| {entry['title'][:80]} | {entry.get('authors', '')[:40]} | {entry.get('year', '')} "
            f"| {entry.get('venue', '')} | {entry.get('url', '')} | auto-scored {score_entry(entry):.1f} |"
            f" <!--h:{h}-->"
        )

    if not rows:
        logger.info("No new entries to append.")
        return 0

    block = f"\n- **{today}** — Auto-crawl appended {appended} new entries.\n" + "\n".join(rows) + "\n"

    if dry_run:
        logger.info("DRY-RUN: would append %d entries.", appended)
        return appended

    brain_text = brain_text.rstrip() + "\n" + block
    with open(brain_path, "w", encoding="utf-8") as fh:
        fh.write(brain_text)

    logger.info("Appended %d new entries to %s", appended, brain_path)
    return appended


# ---------------------------------------------------------------------------
# SEED MODE — authoritative baseline entries (no network required)
# ---------------------------------------------------------------------------
SEED_ENTRIES = [
    {
        "title": "GHG Protocol Corporate Accounting and Reporting Standard",
        "authors": "WRI / WBCSD",
        "year": "2015",
        "venue": "GHG Protocol",
        "url": "https://ghgprotocol.org/corporate-standard",
    },
    {
        "title": "GHG Protocol Scope 3 Calculation Guidance",
        "authors": "WRI / WBCSD",
        "year": "2013",
        "venue": "GHG Protocol",
        "url": "https://ghgprotocol.org/scope-3-technical-calculation-guidance",
    },
    {
        "title": "IPCC 2019 Refinement to the 2006 Guidelines for National GHG Inventories",
        "authors": "IPCC",
        "year": "2019",
        "venue": "IPCC NGGIP",
        "url": "https://www.ipcc-nggip.iges.or.jp/public/2019rf/index.html",
    },
    {
        "title": "ISO 14064-1:2018 Greenhouse gases — Quantification and reporting",
        "authors": "ISO",
        "year": "2018",
        "venue": "ISO",
        "url": "https://www.iso.org/standard/66453.html",
    },
    {
        "title": "ISO 50001:2018 Energy management systems",
        "authors": "ISO",
        "year": "2018",
        "venue": "ISO",
        "url": "https://www.iso.org/standard/69470.html",
    },
    {
        "title": "SBTi Corporate Net-Zero Standard",
        "authors": "Science Based Targets initiative",
        "year": "2021",
        "venue": "SBTi",
        "url": "https://sciencebasedtargets.org/net-zero-standard",
    },
    {
        "title": "SBTi Near-Term Criteria Version 5.0",
        "authors": "Science Based Targets initiative",
        "year": "2023",
        "venue": "SBTi",
        "url": "https://sciencebasedtargets.org/near-term-criteria",
    },
    {
        "title": "IEA World Energy Outlook 2023",
        "authors": "International Energy Agency",
        "year": "2023",
        "venue": "IEA",
        "url": "https://www.iea.org/reports/world-energy-outlook-2023",
    },
    {
        "title": "CDP Global Climate Change Analysis 2023",
        "authors": "CDP Worldwide",
        "year": "2023",
        "venue": "CDP",
        "url": "https://www.cdp.net/en/research/global-reports",
    },
    {
        "title": "Life-Cycle Assessment: Principles and Practice",
        "authors": "U.S. EPA",
        "year": "2006",
        "venue": "EPA",
        "url": "https://www.epa.gov/nrmrl/lcaccess/pdfs/1011_lca_principles.pdf",
    },
    {
        "title": "Marginal Abatement Cost Curves for UK Carbon Reductions",
        "authors": "Cambridge Econometrics / UK CCC",
        "year": "2020",
        "venue": "UK CCC",
        "url": "https://www.theccc.org.uk/publication/macc/",
    },
    {
        "title": "IPCC AR6 WGIII Chapter 12: Cross-sectoral perspectives",
        "authors": "IPCC",
        "year": "2022",
        "venue": "IPCC AR6 WGIII",
        "url": "https://www.ipcc.ch/report/ar6/wg3/",
    },
]


def seed_entries(brain_path=None, dry_run=False):
    '''Append the curated seed set to the knowledge brain.'''
    return append_entries(SEED_ENTRIES, brain_path=brain_path, dry_run=dry_run)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Knowledge brain updater")
    parser.add_argument("--seed", action="store_true", help="append curated seed entries (no network)")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    parser.add_argument("--max-results", type=int, default=25, help="max arXiv results per category")
    parser.add_argument("--brain", default=None, help="path to SECOND-KNOWLEDGE-BRAIN.md")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.seed:
        count = seed_entries(brain_path=args.brain, dry_run=args.dry_run)
        print(f"Seed mode: would append {count} entries" if args.dry_run else f"Seed mode: appended {count} entries")
        return

    entries = fetch_arxiv(ARXIV_CATEGORIES, max_results=args.max_results)
    entries += fetch_websearch(SEARCH_QUERIES)
    count = append_entries(entries, brain_path=args.brain, dry_run=args.dry_run)
    print(f"Dry-run: would append {count} entries" if args.dry_run else f"Appended {count} entries")


if __name__ == "__main__":
    main()
