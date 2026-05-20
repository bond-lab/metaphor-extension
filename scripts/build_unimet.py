"""Build annotation files from the Universal Metonymy (UniMet) dataset.

For each language in UniMet, writes a session JSON file with one item per
polysemous word form and pre-populated metonymy links sourced from UniMet.

Only "full" colexification entries are included: these are cases where a single
word form covers both the source and target concept (true polysemy).

Synset IDs and ILI codes are resolved via omw-en:1.4.

Usage:
    uv run python scripts/build_unimet.py [--unimet PATH] [--out DIR] [--lang ISO ...]

Examples:
    uv run python scripts/build_unimet.py
    uv run python scripts/build_unimet.py --lang eng por fra
    uv run python scripts/build_unimet.py --out docs/data
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import wn

UNIMET_PATH = Path("/home/bond/git/UniMet/UniMet.v1.tsv")
DEFAULT_OUT = Path("annotation")


def safe_filename(value: str) -> str:
    """Sanitize a name for use in a filename."""
    filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in str(value))
    return filename.strip("_") or "session"


def build_ili_cache(offsets: set[str]) -> dict[str, str | None]:
    """Map Princeton WN 3.0 offsets (e.g. 'n00017222') to ILIs via omw-en:1.4.

    Args:
        offsets: Set of offset strings to look up.

    Returns:
        Mapping from offset to ILI string (or None if not found).
    """
    wn_en = wn.Wordnet("omw-en:1.4")
    cache: dict[str, str | None] = {}
    for offset in offsets:
        pos, num = offset[0], offset[1:]
        synset_id = f"omw-en-{num}-{pos}"
        try:
            synset = wn_en.synset(synset_id)
            cache[offset] = synset.ili
        except wn.Error:
            cache[offset] = None
    return cache


def _sense_id(iso: str, word_form: str, offset: str) -> str:
    return f"unimet-{iso}-{word_form}-{offset}"


def _synset_payload(offset: str, translation: str, definition: str, ili: str | None) -> dict:
    pos, num = offset[0], offset[1:]
    return {
        "id": f"omw-en-{num}-{pos}",
        "ili": ili,
        "pos": pos,
        "lemmas": [translation],
        "definition": definition,
    }


def _make_sense(iso: str, word_form: str, offset: str, translation: str, definition: str, ili: str | None) -> dict:
    return {
        "id": _sense_id(iso, word_form, offset),
        "lemma": word_form,
        "word_id": f"unimet-{iso}-{word_form}",
        "synset": _synset_payload(offset, translation, definition, ili),
    }


def build_language_session(
    iso: str,
    language_name: str,
    entries: list[dict],
    ili_cache: dict[str, str | None],
) -> dict:
    """Build an annotation session for one language from UniMet full entries.

    Each item corresponds to one polysemous word form in the language.
    source_senses are the concepts that appear as metonymy source; target_senses
    are the target concepts.  Links are pre-populated with type 'metonymy'.

    Args:
        iso: ISO 639-3 code for the language.
        language_name: Human-readable language name.
        entries: UniMet rows for this language (full colexification only).
        ili_cache: Offset → ILI mapping.

    Returns:
        Session dict compatible with the annotation UI.
    """
    by_word: dict[str, list[dict]] = defaultdict(list)
    for row in entries:
        by_word[row["word_forms"]].append(row)

    items = []
    for word_form in sorted(by_word, key=str.casefold):
        word_entries = by_word[word_form]

        # Collect all unique senses (keyed by offset) and track source/target roles.
        senses_by_offset: dict[str, dict] = {}
        source_offsets: list[str] = []
        target_offsets: list[str] = []

        for row in word_entries:
            src, tgt = row["source_concept_ID"], row["target_concept_ID"]
            if src not in senses_by_offset:
                senses_by_offset[src] = _make_sense(
                    iso, word_form, src,
                    row["source_translation_in_English"],
                    row["source_concept_definition"],
                    ili_cache.get(src),
                )
                source_offsets.append(src)
            if tgt not in senses_by_offset:
                senses_by_offset[tgt] = _make_sense(
                    iso, word_form, tgt,
                    row["target_translation_in_English"],
                    row["target_concept_definition"],
                    ili_cache.get(tgt),
                )
                target_offsets.append(tgt)

        # Pre-populate metonymy links from UniMet.
        links: dict[str, dict] = {}
        for row in word_entries:
            src_id = _sense_id(iso, word_form, row["source_concept_ID"])
            tgt_id = _sense_id(iso, word_form, row["target_concept_ID"])
            key = f"{src_id}::{tgt_id}"
            links[key] = {"source": src_id, "target": tgt_id, "type": "metonymy"}

        all_senses = sorted(senses_by_offset.values(), key=lambda s: s["id"])
        source_senses = [senses_by_offset[o] for o in source_offsets]
        target_senses = [senses_by_offset[o] for o in target_offsets]

        items.append(
            {
                "lemma": word_form,
                "all_senses": all_senses,
                "source_senses": source_senses,
                "target_senses": target_senses,
                "links": links,
                "existing_relations": [],
                "comment": "",
                "sense_annotations": {},
                "status": "open",
            }
        )

    raw = json.dumps(
        {"source": "UniMet.v1", "colexification_type": "full", "iso": iso},
        sort_keys=True,
    )
    session_id = hashlib.sha256(raw.encode()).hexdigest()[:16]

    return {
        "id": session_id,
        "name": f"unimet-{language_name}",
        "wordnet": str(UNIMET_PATH),
        "lexicon": None,
        "display_wordnet": None,
        "display_lexicon": None,
        "unimet_version": "v1",
        "unimet_iso": iso,
        "source_ili": None,
        "target_ili": None,
        "source_roots": [],
        "target_roots": [],
        "items": items,
    }


def load_unimet(path: Path) -> list[dict]:
    """Load UniMet TSV, returning only full colexification rows.

    Args:
        path: Path to UniMet.v1.tsv.

    Returns:
        List of row dicts with colexification_type == 'full'.
    """
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return [row for row in reader if row["colexification_type"] == "full"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--unimet", default=str(UNIMET_PATH), help="Path to UniMet.v1.tsv.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--lang", nargs="+", metavar="ISO", help="Only generate these ISO codes (default: all).")
    args = parser.parse_args()

    unimet_path = Path(args.unimet)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading UniMet …")
    full_rows = load_unimet(unimet_path)

    # Collect all offsets to build ILI cache in one pass.
    all_offsets: set[str] = set()
    for row in full_rows:
        all_offsets.add(row["source_concept_ID"])
        all_offsets.add(row["target_concept_ID"])

    print(f"Mapping {len(all_offsets)} concept IDs to ILIs via omw-en:1.4 …")
    ili_cache = build_ili_cache(all_offsets)
    mapped = sum(1 for v in ili_cache.values() if v)
    print(f"  {mapped}/{len(all_offsets)} mapped successfully")

    # Group by language.
    by_iso: dict[str, list[dict]] = defaultdict(list)
    names: dict[str, str] = {}
    for row in full_rows:
        iso = row["iso"]
        by_iso[iso].append(row)
        names[iso] = row["language"]

    target_isos = set(args.lang) if args.lang else set(by_iso)
    missing = target_isos - set(by_iso)
    if missing:
        print(f"Warning: ISO codes not found in UniMet: {sorted(missing)}")

    written = 0
    for iso in sorted(target_isos & set(by_iso)):
        session = build_language_session(iso, names[iso], by_iso[iso], ili_cache)
        fname = f"{safe_filename(session['name'])}-{session['id']}.json"
        out_path = out_dir / fname
        out_path.write_text(
            json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"  {iso:8s} {names[iso]:40s} {len(session['items']):4d} items → {fname}")
        written += 1

    print(f"\nWrote {written} files to {out_dir}/")


if __name__ == "__main__":
    main()
