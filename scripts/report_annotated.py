"""Report on annotation results from a directory of session JSON files.

Outputs a Markdown report containing:
  1. Summary table (one row per file).
  2. Comparison table against ChainNet and the Metaphor Thesaurus (ILI-based).
  3. Overall confusion matrix: annotated type vs ChainNet type.
  4. Per-file disagreement sections.
  5. Per-file problematic items (ignored, incomplete, comments, bad senses).

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


# ---------------------------------------------------------------------------
# ChainNet index  (OEWN sense key → ILI via oewn:2024)
# ---------------------------------------------------------------------------

def _sk_to_wn(sk: str) -> str:
    """Convert a ChainNet OEWN sense key to the wn library's sense identifier."""
    return "oewn-" + sk.replace("::", "..").replace(":", ".").replace("%", "__")


def build_chainnet_index() -> dict[frozenset, str]:
    """Return {frozenset({ili1, ili2}): link_type} from ChainNet simple files."""
    if not CHAINNET_DIR.exists():
        return {}
    oewn = wn.Wordnet(lexicon="oewn:2024")
    ili_cache: dict[str, str | None] = {}

    def _sk_ili(sk: str) -> str | None:
        if sk not in ili_cache:
            try:
                ili_cache[sk] = oewn.sense(_sk_to_wn(sk)).synset().ili
            except wn.Error:
                ili_cache[sk] = None
        return ili_cache[sk]

    index: dict[frozenset, str] = {}
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
                index[frozenset({src_ili, tgt_ili})] = link_type
    return index


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
    thesaurus: set[frozenset],
) -> dict:
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

    cn_agree = cn_disagree = cn_missing = 0
    th_agree = th_disagree = 0
    confusion: Counter = Counter()   # (our_type, cn_type) for links found in ChainNet
    disagreements = []

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

                if cn_type:
                    confusion[(link_type, cn_type)] += 1
                    if cn_type == link_type:
                        cn_agree += 1
                    else:
                        cn_disagree += 1
                        disagreements.append((
                            item.get("lemma", "?"), link_type, cn_type,
                            in_thesaurus, lnk["source"], lnk["target"],
                        ))
                else:
                    cn_missing += 1

                if in_thesaurus:
                    if link_type == "metaphor":
                        th_agree += 1
                    else:
                        th_disagree += 1
                        if not cn_type:
                            disagreements.append((
                                item.get("lemma", "?"), link_type, None,
                                True, lnk["source"], lnk["target"],
                            ))

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
        "cn_disagree": cn_disagree,
        "cn_missing": cn_missing,
        "th_agree": th_agree,
        "th_disagree": th_disagree,
        "confusion": confusion,
        "disagreements": disagreements,
    }


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def _md_cell(s: str) -> str:
    return str(s).replace("|", "\\|")


def _md_table(headers: list[str], rows: list[list]) -> list[str]:
    lines = ["| " + " | ".join(_md_cell(h) for h in headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_md_cell(c) for c in row) + " |")
    return lines


def _sense_label(sense_id: str, session: dict) -> str:
    for item in session.get("items", []):
        for s in item.get("all_senses", []):
            if s["id"] == sense_id:
                syn = s.get("synset", {})
                lemmas = syn.get("lemmas", [])
                defn = syn.get("definition", "")
                label = lemmas[0] if lemmas else sense_id
                if defn:
                    label += f" — {defn[:70]}{'…' if len(defn) > 70 else ''}"
                return label
    return sense_id


# ---------------------------------------------------------------------------
# Report sections (all output Markdown)
# ---------------------------------------------------------------------------

def print_summary_table(rows: list[dict], files: list[Path], out=sys.stdout) -> None:
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
    print("\n## Comparison with ChainNet and Metaphor Thesaurus\n", file=out)
    print("ILI-based matching: same unordered synset pair = match, regardless of direction.\n", file=out)
    print("- **CN=** agree with ChainNet  **CN≠** disagree  **CN?** not in ChainNet", file=out)
    print("- **TH=** pair found in Metaphor Thesaurus (all thesaurus entries are metaphor)  **TH≠** found but type differs\n", file=out)
    headers = ["File", "Links", "CN=", "CN≠", "CN?", "TH=", "TH≠"]
    table_rows = [
        [
            fname.stem,
            sum(r["link_counts"].values()),
            r["cn_agree"], r["cn_disagree"], r["cn_missing"],
            r["th_agree"], r["th_disagree"],
        ]
        for fname, r in zip(files, rows)
    ]
    for line in _md_table(headers, table_rows):
        print(line, file=out)


def print_confusion_matrix(rows: list[dict], out=sys.stdout) -> None:
    """Print an overall confusion matrix: annotated type (rows) vs ChainNet type (cols)."""
    print("\n## Confusion Matrix: Annotation vs ChainNet\n", file=out)
    print("Rows = our annotation, Columns = ChainNet label.", file=out)
    print("Only links where ChainNet has an opinion are included.\n", file=out)

    combined: Counter = Counter()
    for r in rows:
        combined.update(r["confusion"])

    # Row totals per our annotation type
    our_types = LINK_TYPES
    headers = ["Our \\ ChainNet"] + CN_TYPES + ["**Row total**"]
    table_rows = []
    for our in our_types:
        row_total = sum(combined[(our, cn)] for cn in CN_TYPES)
        if row_total == 0:
            continue
        table_rows.append(
            [f"**{our}**"] + [combined[(our, cn)] for cn in CN_TYPES] + [f"**{row_total}**"]
        )
    col_totals = [sum(combined[(our, cn)] for our in our_types) for cn in CN_TYPES]
    grand = sum(col_totals)
    table_rows.append(["**Col total**"] + [f"**{t}**" for t in col_totals] + [f"**{grand}**"])

    for line in _md_table(headers, table_rows):
        print(line, file=out)


def print_disagreement_sections(
    rows: list[dict], files: list[Path], sessions: list[dict], out=sys.stdout
) -> None:
    any_disagreements = any(r["disagreements"] for r in rows)
    if not any_disagreements:
        return
    print("\n## Disagreements with ChainNet / Thesaurus\n", file=out)
    for fname, r, session in zip(files, rows, sessions):
        if not r["disagreements"]:
            continue
        print(f"### {fname.stem} ({r['name']})\n", file=out)
        for lemma, our_type, cn_type, in_thesaurus, src_id, tgt_id in r["disagreements"]:
            src_lbl = _sense_label(src_id, session)
            tgt_lbl = _sense_label(tgt_id, session)
            th_note = " *(also in thesaurus as metaphor)*" if in_thesaurus else ""
            if cn_type:
                print(f"- **{lemma}**: annotated `{our_type}` but ChainNet has `{cn_type}`{th_note}", file=out)
            else:
                print(f"- **{lemma}**: annotated `{our_type}` but thesaurus says `metaphor`", file=out)
            print(f"  - {src_lbl}", file=out)
            print(f"  - → {tgt_lbl}", file=out)
        print(file=out)


def print_problem_sections(
    rows: list[dict], files: list[Path], sessions: list[dict], out=sys.stdout
) -> None:
    print("\n## Problematic Items\n", file=out)
    any_problems = any(r["problems"] for r in rows)
    if not any_problems:
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
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

    if args.no_compare:
        chainnet: dict[frozenset, str] = {}
        thesaurus: set[frozenset] = set()
    else:
        print("Loading ChainNet index …", file=sys.stderr)
        chainnet = build_chainnet_index()
        print(f"  {len(chainnet)} ILI pairs indexed", file=sys.stderr)
        print("Loading Metaphor Thesaurus index …", file=sys.stderr)
        thesaurus = build_thesaurus_index()
        print(f"  {len(thesaurus)} ILI pairs indexed", file=sys.stderr)

    rows = [analyse_session(s, chainnet, thesaurus) for s in sessions]

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
        print_problem_sections(rows, files, sessions, out=fh)

    with report_path.open("w", encoding="utf-8") as fh:
        _write(fh)
    _write(sys.stdout)
    print(f"\nReport saved to {report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
