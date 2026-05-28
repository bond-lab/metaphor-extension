"""Report on annotation results from a directory of session JSON files.

Outputs a Markdown report containing:
  1. Summary table (one row per file).
  2. Comparison table against ChainNet and the Metaphor Thesaurus (ILI-based).
  3. Overall confusion matrix: annotated type vs ChainNet type.
  4. Per-file disagreement sections (type and direction).
  5. Per-file differences from UniMet baseline (where we changed UniMet's suggestions).
  6. Per-file problematic items (ignored, incomplete, comments, bad senses).
  7. Per-file agreement sections.

Usage:
    uv run python scripts/report_annotated.py [DIR] [--out DIR] [--no-compare]

DIR defaults to 'annotated'.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import wn

LINK_TYPES = ["metaphor", "metonymy", "hypernym", "other"]
CN_TYPES = ["metaphor", "metonymy"]
PROBLEM_STATUSES = {"incomplete", "ignore"}

CHAINNET_DIR = Path("/home/bond/git/ChainNet/data/chainnet_simple")
THESAURUS_WN = Path("/home/bond/git/metaphor-thesaurus/build/thesaurus_wn.json")
BASELINE_DIR = Path("annotation")


# ---------------------------------------------------------------------------
# ChainNet index  (OEWN sense key → ILI via oewn:2024)
# ---------------------------------------------------------------------------

def _sk_to_wn(sk: str) -> str:
    """Convert a ChainNet OEWN sense key to the wn library's sense identifier."""
    return "oewn-" + sk.replace("::", "..").replace(":", ".").replace("%", "__")


def build_chainnet_index() -> tuple[dict[frozenset, str], dict[tuple[str, str], str]]:
    """Return (undirected, directed) ChainNet indices.

    undirected: {frozenset({ili1, ili2}): link_type}
    directed: {(from_ili, to_ili): link_type}

    Returns:
        Tuple of (undirected_index, directed_index).
    """
    if not CHAINNET_DIR.exists():
        return {}, {}
    oewn = wn.Wordnet(lexicon="oewn:2024")
    ili_cache: dict[str, str | None] = {}

    def _sk_ili(sk: str) -> str | None:
        if sk not in ili_cache:
            try:
                ili_cache[sk] = oewn.sense(_sk_to_wn(sk)).synset().ili
            except wn.Error:
                ili_cache[sk] = None
        return ili_cache[sk]

    undirected: dict[frozenset, str] = {}
    directed: dict[tuple[str, str], str] = {}
    for fname, link_type in [
        ("chainnet_metaphor.json", "metaphor"),
        ("chainnet_metonymy.json", "metonymy"),
    ]:
        path = CHAINNET_DIR / fname
        if not path.exists():
            continue
        for entry in json.loads(path.read_text(encoding="utf-8"))["content"]:
            src_ili = _sk_ili(entry["from_sense"])
            tgt_ili = _sk_ili(entry["to_sense"])
            if src_ili and tgt_ili and src_ili != tgt_ili:
                key = frozenset({src_ili, tgt_ili})
                undirected[key] = link_type
                directed[(src_ili, tgt_ili)] = link_type
    return undirected, directed


# ---------------------------------------------------------------------------
# Metaphor-thesaurus index  (omw-en synset IDs → ILI via omw-en:1.4)
# ---------------------------------------------------------------------------

def build_thesaurus_index() -> set[frozenset]:
    """Return a set of frozenset({ili1, ili2}) for all metaphor pairs in the thesaurus."""
    if not THESAURUS_WN.exists():
        return set()
    omw = wn.Wordnet(lexicon="omw-en:1.4")
    ili_cache: dict[str, str | None] = {}

    def _syn_ili(synset_id: str) -> str | None:
        if synset_id not in ili_cache:
            try:
                ili_cache[synset_id] = omw.synset(synset_id).ili
            except wn.Error:
                ili_cache[synset_id] = None
        return ili_cache[synset_id]

    data = json.loads(THESAURUS_WN.read_text(encoding="utf-8"))
    pairs: set[frozenset] = set()
    for part in data["parts"]:
        for theme in part["themes"]:
            for sub in theme.get("subsections", []):
                for entry in sub.get("entries", []):
                    lit = (entry.get("wn_literal") or {}).get("synset_id")
                    meta = (entry.get("wn_metaphorical") or {}).get("synset_id")
                    if not lit or not meta or lit == meta:
                        continue
                    ili_lit, ili_meta = _syn_ili(lit), _syn_ili(meta)
                    if ili_lit and ili_meta and ili_lit != ili_meta:
                        pairs.add(frozenset({ili_lit, ili_meta}))
    return pairs


# ---------------------------------------------------------------------------
# UniMet baseline comparison
# ---------------------------------------------------------------------------

def load_unimet_baselines(sessions: list[dict]) -> dict[str, dict]:
    """Find original UniMet session files matching sessions with unimet_version set.

    Searches BASELINE_DIR for JSON files whose 'id' matches the session id.

    Args:
        sessions: List of annotated sessions to match against.

    Returns:
        Mapping from session id to original session dict.
    """
    if not BASELINE_DIR.is_dir():
        return {}
    baseline_by_id: dict[str, dict] = {}
    for f in BASELINE_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if sid := data.get("id"):
                baseline_by_id[sid] = data
        except (json.JSONDecodeError, KeyError):
            continue
    return {
        session["id"]: baseline_by_id[session["id"]]
        for session in sessions
        if session.get("unimet_version") and session.get("id") in baseline_by_id
    }


def compare_with_baseline(session: dict, baseline: dict) -> list[dict]:
    """Return list of differences between annotated session and UniMet baseline.

    Each difference dict has keys: lemma, kind, our_type, baseline_type, src_id, tgt_id.
    kind is one of: 'type_changed', 'removed', 'added'.

    Args:
        session: Annotated session dict.
        baseline: Original UniMet session dict.

    Returns:
        List of difference dicts, one per changed link.
    """
    baseline_items = {item["lemma"]: item for item in baseline.get("items", [])}
    diffs: list[dict] = []

    for item in session.get("items", []):
        lemma = item.get("lemma", "?")
        our_links = item.get("links", {})
        baseline_links = (baseline_items.get(lemma) or {}).get("links", {})

        for key in set(our_links) | set(baseline_links):
            our_lnk = our_links.get(key)
            base_lnk = baseline_links.get(key)

            if our_lnk and base_lnk:
                if our_lnk["type"] != base_lnk["type"]:
                    diffs.append({
                        "lemma": lemma,
                        "kind": "type_changed",
                        "our_type": our_lnk["type"],
                        "baseline_type": base_lnk["type"],
                        "src_id": our_lnk["source"],
                        "tgt_id": our_lnk["target"],
                    })
            elif our_lnk:
                diffs.append({
                    "lemma": lemma,
                    "kind": "added",
                    "our_type": our_lnk["type"],
                    "baseline_type": None,
                    "src_id": our_lnk["source"],
                    "tgt_id": our_lnk["target"],
                })
            else:
                diffs.append({
                    "lemma": lemma,
                    "kind": "removed",
                    "our_type": None,
                    "baseline_type": base_lnk["type"],
                    "src_id": base_lnk["source"],
                    "tgt_id": base_lnk["target"],
                })
    return diffs


# ---------------------------------------------------------------------------
# Session analysis
# ---------------------------------------------------------------------------

def _potential_pairs(item: dict) -> int:
    src_ids = {s["id"] for s in item.get("source_senses", [])}
    tgt_ids = {s["id"] for s in item.get("target_senses", [])}
    return sum(1 for s in src_ids for t in tgt_ids if s != t)


def _build_ili_map(session: dict) -> dict[str, str | None]:
    return {
        s["id"]: s.get("synset", {}).get("ili")
        for item in session.get("items", [])
        for s in item.get("all_senses", [])
    }


def analyse_session(
    session: dict,
    chainnet: dict[frozenset, str],
    directed_chainnet: dict[tuple[str, str], str],
    thesaurus: set[frozenset],
) -> dict:
    """Return analysis dict for one session.

    Args:
        session: Session dict with items and links.
        chainnet: Undirected ILI pair → ChainNet link type.
        directed_chainnet: Directed (from_ili, to_ili) → ChainNet link type.
        thesaurus: Set of frozenset ILI pairs in the Metaphor Thesaurus.

    Returns:
        Analysis dict with counts, problems, disagreements, and agreements.
    """
    items = session.get("items", [])
    n_senses = sum(len(i.get("all_senses", [])) for i in items)
    n_pairs = sum(_potential_pairs(i) for i in items)

    link_counts: Counter = Counter()
    n_annotated = 0
    status_counts: Counter = Counter()
    n_bad_senses = 0
    n_comments = 0
    problems = []

    cn_agree = cn_dir_disagree = cn_type_disagree = cn_missing = 0
    th_agree = th_disagree = 0
    confusion: Counter = Counter()
    disagreements: list[dict] = []
    agreements: list[dict] = []

    ili_map = _build_ili_map(session)

    for item in items:
        links = item.get("links", {})
        status = item.get("status", "open")
        comment = (item.get("comment") or "").strip()
        sense_ann = item.get("sense_annotations", {})

        for lnk in links.values():
            link_type = lnk.get("type", "?")
            link_counts[link_type] += 1

            src_ili = ili_map.get(lnk["source"])
            tgt_ili = ili_map.get(lnk["target"])
            if src_ili and tgt_ili and src_ili != tgt_ili:
                key = frozenset({src_ili, tgt_ili})
                cn_type = chainnet.get(key)
                in_thesaurus = key in thesaurus
                same_dir = (src_ili, tgt_ili) in directed_chainnet

                if cn_type:
                    confusion[(link_type, cn_type)] += 1
                    if cn_type == link_type:
                        if same_dir:
                            cn_agree += 1
                            agreements.append({
                                "lemma": item.get("lemma", "?"),
                                "our_type": link_type,
                                "cn_type": cn_type,
                                "in_thesaurus": in_thesaurus,
                                "src_id": lnk["source"],
                                "tgt_id": lnk["target"],
                                "source": "chainnet",
                            })
                        else:
                            cn_dir_disagree += 1
                            disagreements.append({
                                "lemma": item.get("lemma", "?"),
                                "our_type": link_type,
                                "cn_type": cn_type,
                                "in_thesaurus": in_thesaurus,
                                "src_id": lnk["source"],
                                "tgt_id": lnk["target"],
                                "kind": "direction",
                            })
                    else:
                        cn_type_disagree += 1
                        disagreements.append({
                            "lemma": item.get("lemma", "?"),
                            "our_type": link_type,
                            "cn_type": cn_type,
                            "in_thesaurus": in_thesaurus,
                            "src_id": lnk["source"],
                            "tgt_id": lnk["target"],
                            "kind": "type",
                        })
                else:
                    cn_missing += 1

                if in_thesaurus:
                    if link_type == "metaphor":
                        th_agree += 1
                        if not cn_type:
                            agreements.append({
                                "lemma": item.get("lemma", "?"),
                                "our_type": link_type,
                                "cn_type": None,
                                "in_thesaurus": True,
                                "src_id": lnk["source"],
                                "tgt_id": lnk["target"],
                                "source": "thesaurus",
                            })
                    else:
                        th_disagree += 1
                        if not cn_type:
                            disagreements.append({
                                "lemma": item.get("lemma", "?"),
                                "our_type": link_type,
                                "cn_type": None,
                                "in_thesaurus": True,
                                "src_id": lnk["source"],
                                "tgt_id": lnk["target"],
                                "kind": "thesaurus",
                            })

        if links:
            n_annotated += 1
        status_counts[status] += 1

        bad_senses = {sid: ann for sid, ann in sense_ann.items() if ann.get("bad_sense")}
        sense_comments = {
            sid: ann["comment"] for sid, ann in sense_ann.items()
            if ann.get("comment", "").strip()
        }
        n_bad_senses += len(bad_senses)
        if comment:
            n_comments += 1

        if status in PROBLEM_STATUSES or comment or bad_senses or sense_comments:
            problems.append({
                "lemma": item.get("lemma", "?"),
                "status": status,
                "comment": comment,
                "bad_senses": bad_senses,
                "sense_comments": sense_comments,
                "links": links,
            })

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
        "cn_agree": cn_agree,
        "cn_dir_disagree": cn_dir_disagree,
        "cn_type_disagree": cn_type_disagree,
        "cn_missing": cn_missing,
        "th_agree": th_agree,
        "th_disagree": th_disagree,
        "confusion": confusion,
        "disagreements": disagreements,
        "agreements": agreements,
    }


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def _md_cell(s: str) -> str:
    """Escape pipe characters for Markdown tables."""
    return str(s).replace("|", "\\|")


def _md_table(headers: list[str], rows: list[list]) -> list[str]:
    """Render a Markdown table from headers and rows."""
    lines = ["| " + " | ".join(_md_cell(h) for h in headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_md_cell(c) for c in row) + " |")
    return lines


def _sense_label(sense_id: str, session: dict) -> str:
    """Build a human-readable label for a sense ID."""
    for item in session.get("items", []):
        for s in item.get("all_senses", []):
            if s["id"] == sense_id:
                syn = s.get("synset", {})
                lemmas = syn.get("lemmas", [])
                defn = syn.get("definition", "")
                label = lemmas[0] if lemmas else sense_id
                if defn:
                    label += f" — {defn}"
                return label
    return sense_id


# ---------------------------------------------------------------------------
# Report sections (all output Markdown)
# ---------------------------------------------------------------------------

def print_summary_table(rows: list[dict], files: list[Path], out=sys.stdout) -> None:
    """Print the summary table section."""
    print("## Summary\n", file=out)
    headers = [
        "File", "Items", "Senses", "Pairs", "Ann",
        "Done", "Part", "Ign", "Open", "BadS", "Cmts",
        *LINK_TYPES,
    ]
    table_rows = []
    for fname, r in zip(files, rows):
        sc = r["status_counts"]
        lc = r["link_counts"]
        table_rows.append([
            fname.stem,
            r["n_items"], r["n_senses"], r["n_pairs"], r["n_annotated"],
            sc.get("done", 0), sc.get("incomplete", 0),
            sc.get("ignore", 0), sc.get("open", 0),
            r["n_bad_senses"], r["n_comments"],
            *[lc.get(t, 0) for t in LINK_TYPES],
        ])
    for line in _md_table(headers, table_rows):
        print(line, file=out)


def print_comparison_table(rows: list[dict], files: list[Path], out=sys.stdout) -> None:
    """Print the ChainNet / Metaphor Thesaurus comparison table."""
    print("\n## Comparison with ChainNet and Metaphor Thesaurus\n", file=out)
    print("ILI-based matching: same unordered synset pair = match, regardless of direction.\n", file=out)
    print("- **CN=** agree with ChainNet (same type, same direction)", file=out)
    print("- **CN↔** same type but opposite direction", file=out)
    print("- **CN≠** type disagrees  **CN?** not in ChainNet", file=out)
    print("- **TH=** pair in Metaphor Thesaurus (all thesaurus entries are metaphor)"
          "  **TH≠** found but type differs\n", file=out)
    headers = ["File", "Links", "CN=", "CN↔", "CN≠", "CN?", "TH=", "TH≠"]
    table_rows = [
        [
            fname.stem,
            sum(r["link_counts"].values()),
            r["cn_agree"], r["cn_dir_disagree"], r["cn_type_disagree"], r["cn_missing"],
            r["th_agree"], r["th_disagree"],
        ]
        for fname, r in zip(files, rows)
    ]
    for line in _md_table(headers, table_rows):
        print(line, file=out)


def print_confusion_matrix(rows: list[dict], out=sys.stdout) -> None:
    """Print overall confusion matrix: annotated type (rows) vs ChainNet type (cols)."""
    print("\n## Confusion Matrix: Annotation vs ChainNet\n", file=out)
    print("Rows = our annotation, Columns = ChainNet label.", file=out)
    print("Only links where ChainNet has an opinion are included.\n", file=out)

    combined: Counter = Counter()
    for r in rows:
        combined.update(r["confusion"])

    headers = ["Our \\ ChainNet"] + CN_TYPES + ["Row total"]
    table_rows = []
    for our in LINK_TYPES:
        row_total = sum(combined[(our, cn)] for cn in CN_TYPES)
        if row_total == 0:
            continue
        cells = [
            f"**{combined[(our, cn)]}**" if our == cn else str(combined[(our, cn)])
            for cn in CN_TYPES
        ]
        table_rows.append([our] + cells + [str(row_total)])

    col_totals = [sum(combined[(our, cn)] for our in LINK_TYPES) for cn in CN_TYPES]
    grand = sum(col_totals)
    table_rows.append(["Col total"] + [str(t) for t in col_totals] + [str(grand)])

    for line in _md_table(headers, table_rows):
        print(line, file=out)


def print_disagreement_sections(
    rows: list[dict], files: list[Path], sessions: list[dict], out=sys.stdout
) -> None:
    """Print per-file disagreement sections (type and direction)."""
    if not any(r["disagreements"] for r in rows):
        return
    print("\n## Disagreements with ChainNet / Thesaurus\n", file=out)
    for fname, r, session in zip(files, rows, sessions):
        if not r["disagreements"]:
            continue
        print(f"### {fname.stem} ({r['name']})\n", file=out)
        for d in r["disagreements"]:
            src_lbl = _sense_label(d["src_id"], session)
            tgt_lbl = _sense_label(d["tgt_id"], session)
            th_note = " *(also in thesaurus as metaphor)*" if d["in_thesaurus"] else ""
            lemma, our_type, cn_type = d["lemma"], d["our_type"], d["cn_type"]

            if d["kind"] == "type":
                print(f"- **{lemma}**: annotated `{our_type}` but ChainNet has `{cn_type}`{th_note}", file=out)
            elif d["kind"] == "direction":
                print(
                    f"- **{lemma}**: annotated `{our_type}` (A→B) but ChainNet has"
                    f" `{cn_type}` in opposite direction (B→A){th_note}",
                    file=out,
                )
            else:  # thesaurus
                print(f"- **{lemma}**: annotated `{our_type}` but thesaurus says `metaphor`", file=out)
            print(f"  - {src_lbl}", file=out)
            print(f"  - → {tgt_lbl}", file=out)
        print(file=out)


def print_unimet_diff_sections(
    rows: list[dict], files: list[Path], sessions: list[dict],
    baselines: dict[str, dict], out=sys.stdout,
) -> None:
    """Print sections comparing annotated UniMet sessions against their original baseline."""
    relevant = [
        (fname, r, session)
        for fname, r, session in zip(files, rows, sessions)
        if session.get("unimet_version") and session.get("id") in baselines
    ]
    if not relevant:
        return
    print("\n## Differences from UniMet Baseline\n", file=out)
    print(
        "Compares our annotations against UniMet's pre-populated metonymy links.\n"
        "- **type_changed**: we chose a different link type\n"
        "- **removed**: UniMet had a link; we removed it\n"
        "- **added**: we created a link not in UniMet\n",
        file=out,
    )
    for fname, r, session in relevant:
        baseline = baselines[session["id"]]
        diffs = compare_with_baseline(session, baseline)
        print(f"### {fname.stem} ({r['name']})\n", file=out)
        if not diffs:
            print("No differences from UniMet baseline.\n", file=out)
            continue
        for d in diffs:
            src_lbl = _sense_label(d["src_id"], session)
            tgt_lbl = _sense_label(d["tgt_id"], session)
            lemma, kind = d["lemma"], d["kind"]

            if kind == "type_changed":
                print(
                    f"- **{lemma}**: UniMet `{d['baseline_type']}` → we annotated `{d['our_type']}`",
                    file=out,
                )
            elif kind == "removed":
                print(
                    f"- **{lemma}**: UniMet had `{d['baseline_type']}` — we removed this link",
                    file=out,
                )
            else:
                print(
                    f"- **{lemma}**: we added `{d['our_type']}` (not in UniMet baseline)",
                    file=out,
                )
            print(f"  - {src_lbl}", file=out)
            print(f"  - → {tgt_lbl}", file=out)
        print(file=out)


def print_problem_sections(
    rows: list[dict], files: list[Path], sessions: list[dict], out=sys.stdout
) -> None:
    """Print per-file problematic items sections."""
    print("\n## Problematic Items\n", file=out)
    if not any(r["problems"] for r in rows):
        print("No problematic items.", file=out)
        return
    for fname, r, session in zip(files, rows, sessions):
        if not r["problems"]:
            continue
        print(f"### {fname.stem} ({r['name']})\n", file=out)
        for p in r["problems"]:
            print(f"**{p['lemma']}** — status: `{p['status']}`\n", file=out)
            if p["comment"]:
                print(f"> {p['comment']}\n", file=out)
            for sid, ann in p["bad_senses"].items():
                note = ann.get("comment", "").strip()
                print(f"- Bad sense: {_sense_label(sid, session)}", file=out)
                if note:
                    print(f"  - ↳ {note}", file=out)
            for sid, cmt in p["sense_comments"].items():
                if sid not in p["bad_senses"]:
                    print(f"- Sense comment on {_sense_label(sid, session)}: {cmt}", file=out)
            if p["links"]:
                print("- Links annotated:", file=out)
                for lnk in p["links"].values():
                    src = _sense_label(lnk["source"], session)
                    tgt = _sense_label(lnk["target"], session)
                    print(f"  - `{lnk['type']}` {src} → {tgt}", file=out)
            print(file=out)


def print_agreement_sections(
    rows: list[dict], files: list[Path], sessions: list[dict], out=sys.stdout
) -> None:
    """Print per-file agreement sections."""
    print("\n## Agreements with ChainNet / Thesaurus\n", file=out)
    if not any(r["agreements"] for r in rows):
        print("No agreements found.", file=out)
        return
    for fname, r, session in zip(files, rows, sessions):
        if not r["agreements"]:
            continue
        print(f"### {fname.stem} ({r['name']})\n", file=out)
        for agr in r["agreements"]:
            src_lbl = _sense_label(agr["src_id"], session)
            tgt_lbl = _sense_label(agr["tgt_id"], session)
            lemma, our_type = agr["lemma"], agr["our_type"]
            th_note = " *(also in thesaurus)*" if agr["in_thesaurus"] and agr["source"] == "chainnet" else ""

            if agr["source"] == "chainnet":
                print(f"- **{lemma}**: `{our_type}` agrees with ChainNet{th_note}", file=out)
            else:
                print(f"- **{lemma}**: `{our_type}` agrees with Thesaurus", file=out)
            print(f"  - {src_lbl}", file=out)
            print(f"  - → {tgt_lbl}", file=out)
        print(file=out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dir", nargs="?", default="annotated",
                        help="Directory containing annotated session JSON files.")
    parser.add_argument("--out", default="reports",
                        help="Output directory (default: reports/).")
    parser.add_argument("--no-compare", action="store_true",
                        help="Skip ChainNet / thesaurus comparison (faster).")
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

    print("Loading UniMet baselines …", file=sys.stderr)
    baselines = load_unimet_baselines(sessions)
    print(f"  {len(baselines)} baseline(s) matched", file=sys.stderr)

    if args.no_compare:
        chainnet: dict[frozenset, str] = {}
        directed_chainnet: dict[tuple[str, str], str] = {}
        thesaurus: set[frozenset] = set()
    else:
        print("Loading ChainNet index …", file=sys.stderr)
        chainnet, directed_chainnet = build_chainnet_index()
        print(f"  {len(chainnet)} ILI pairs indexed", file=sys.stderr)
        print("Loading Metaphor Thesaurus index …", file=sys.stderr)
        thesaurus = build_thesaurus_index()
        print(f"  {len(thesaurus)} ILI pairs indexed", file=sys.stderr)

    rows = [analyse_session(s, chainnet, directed_chainnet, thesaurus) for s in sessions]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{directory.name}.md"

    def _write(fh) -> None:
        print(f"# Annotation Report: {directory.name}\n", file=fh)
        print_summary_table(rows, files, out=fh)
        if not args.no_compare:
            print_comparison_table(rows, files, out=fh)
            print_confusion_matrix(rows, out=fh)
            print_disagreement_sections(rows, files, sessions, out=fh)
        print_unimet_diff_sections(rows, files, sessions, baselines, out=fh)
        print_problem_sections(rows, files, sessions, out=fh)
        if not args.no_compare:
            print_agreement_sections(rows, files, sessions, out=fh)

    with report_path.open("w", encoding="utf-8") as fh:
        _write(fh)
    _write(sys.stdout)
    print(f"\nReport saved to {report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
