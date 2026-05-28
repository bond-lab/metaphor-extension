"""Report on annotation results from a directory of session JSON files.

Prints:
  1. A summary table (one row per file).
  2. A per-file section listing every problematic item (ignored, incomplete,
     has a comment, or contains a bad sense).

Usage:
    uv run python scripts/report_annotated.py [DIR]

DIR defaults to 'annotated'.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

LINK_TYPES = ["metaphor", "metonymy", "hypernym", "other"]
PROBLEM_STATUSES = {"incomplete", "ignore"}


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------

def _potential_pairs(item: dict) -> int:
    """Count directed (src, tgt) sense pairs where src != tgt."""
    src_ids = {s["id"] for s in item.get("source_senses", [])}
    tgt_ids = {s["id"] for s in item.get("target_senses", [])}
    return sum(1 for s in src_ids for t in tgt_ids if s != t)


def analyse_session(session: dict) -> dict:
    """Return analysis dict for one session."""
    items = session.get("items", [])
    n_senses = sum(len(i.get("all_senses", [])) for i in items)
    n_pairs = sum(_potential_pairs(i) for i in items)

    link_counts: Counter = Counter()
    n_annotated = 0
    status_counts: Counter = Counter()
    n_bad_senses = 0
    n_comments = 0
    problems = []

    for item in items:
        links = item.get("links", {})
        status = item.get("status", "open")
        comment = (item.get("comment") or "").strip()
        sense_ann = item.get("sense_annotations", {})

        for lnk in links.values():
            link_counts[lnk.get("type", "?")] += 1
        if links:
            n_annotated += 1
        status_counts[status] += 1

        bad_senses = {sid: ann for sid, ann in sense_ann.items() if ann.get("bad_sense")}
        sense_comments = {sid: ann["comment"] for sid, ann in sense_ann.items()
                          if ann.get("comment", "").strip()}
        n_bad_senses += len(bad_senses)
        if comment:
            n_comments += 1

        is_problem = (
            status in PROBLEM_STATUSES
            or comment
            or bad_senses
            or sense_comments
        )
        if is_problem:
            problems.append(
                {
                    "lemma": item.get("lemma", "?"),
                    "status": status,
                    "comment": comment,
                    "bad_senses": bad_senses,
                    "sense_comments": sense_comments,
                    "links": links,
                }
            )

    return {
        "name": session.get("name", "?"),
        "n_items": len(items),
        "n_senses": n_senses,
        "n_pairs": n_pairs,
        "n_annotated": n_annotated,
        "status_counts": status_counts,
        "link_counts": link_counts,
        "n_bad_senses": n_bad_senses,
        "n_comments": n_comments,
        "problems": problems,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _sense_label(sense_id: str, session: dict) -> str:
    """Return a short human label for a sense id."""
    for item in session.get("items", []):
        for s in item.get("all_senses", []):
            if s["id"] == sense_id:
                syn = s.get("synset", {})
                lemmas = syn.get("lemmas", [])
                defn = syn.get("definition", "")
                label = lemmas[0] if lemmas else sense_id
                if defn:
                    label += f" — {defn[:60]}{'…' if len(defn) > 60 else ''}"
                return label
    return sense_id


def _format_links(links: dict, session: dict) -> list[str]:
    lines = []
    for lnk in links.values():
        src = _sense_label(lnk["source"], session)
        tgt = _sense_label(lnk["target"], session)
        lines.append(f"      [{lnk['type']}]  {src}  →  {tgt}")
    return lines


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_summary_table(rows: list[dict], files: list[Path]) -> None:
    # Header
    lt_cols = "  ".join(f"{t:>9}" for t in LINK_TYPES)
    header = (
        f"{'File':<32}  {'Items':>5}  {'Senses':>6}  {'Pairs':>6}  "
        f"{'Ann':>5}  {'Done':>5}  {'Part':>5}  {'Ign':>5}  {'Open':>5}  "
        f"{'BadS':>4}  {'Cmts':>4}  {lt_cols}"
    )
    print(header)
    print("-" * len(header))

    for fname, r in zip(files, rows):
        sc = r["status_counts"]
        lc = r["link_counts"]
        lt_vals = "  ".join(f"{lc.get(t, 0):>9}" for t in LINK_TYPES)
        print(
            f"{fname.stem[:32]:<32}  {r['n_items']:>5}  {r['n_senses']:>6}  "
            f"{r['n_pairs']:>6}  {r['n_annotated']:>5}  "
            f"{sc.get('done', 0):>5}  {sc.get('incomplete', 0):>5}  "
            f"{sc.get('ignore', 0):>5}  {sc.get('open', 0):>5}  "
            f"{r['n_bad_senses']:>4}  {r['n_comments']:>4}  {lt_vals}"
        )


def print_problem_sections(rows: list[dict], files: list[Path], sessions: list[dict]) -> None:
    for fname, r, session in zip(files, rows, sessions):
        if not r["problems"]:
            continue
        print(f"\n{'='*70}")
        print(f"  {fname.name}  ({r['name']})")
        print(f"{'='*70}")
        for p in r["problems"]:
            print(f"\n  Lemma: {p['lemma']}   status={p['status']}")
            if p["comment"]:
                print(f"    Comment: {p['comment']}")
            for sid, ann in p["bad_senses"].items():
                note = ann.get("comment", "").strip()
                label = _sense_label(sid, session)
                print(f"    Bad sense: {label}")
                if note:
                    print(f"      ↳ {note}")
            for sid, cmt in p["sense_comments"].items():
                if sid not in p["bad_senses"]:
                    label = _sense_label(sid, session)
                    print(f"    Sense comment on {label}: {cmt}")
            if p["links"]:
                print("    Links annotated:")
                for line in _format_links(p["links"], session):
                    print(line)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dir", nargs="?", default="annotated",
                        help="Directory containing annotated session JSON files.")
    args = parser.parse_args()

    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory.", file=sys.stderr)
        sys.exit(1)

    files = sorted(directory.glob("*.json"))
    if not files:
        print(f"No JSON files found in {directory}.", file=sys.stderr)
        sys.exit(1)

    sessions = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    rows = [analyse_session(s) for s in sessions]

    print_summary_table(rows, files)
    print_problem_sections(rows, files, sessions)


if __name__ == "__main__":
    main()
