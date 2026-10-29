#!/usr/bin/env python3
"""Pre-fill the PERSON is ANIMAL class spreadsheet for one language.

The class sheet lists English animal/person sense pairs with ``omw-en`` sense
ids.  For a target wordnet this script looks each pair up and fills in:

- ``Language``: the target lemma(s) that carry *both* senses, or failing that
  the translation of the animal sense;
- ``Checked (Y/N)``: ``Y`` when a single lemma carries both senses, otherwise
  left blank for the student to decide;
- ``Comment``: an ``auto:`` note saying what the wordnet knows.

With ``--extras`` it appends any further animal/person colexifications found in
the target wordnet that the sheet does not already list.

Translations can come from a wordnet (``--wordnet``), from the ARASAAC
pictogram keywords for a language (``--arasaac ko``), or both.  ARASAAC
pictograms carry WordNet 3.1 synset ids, which are mapped to ILIs through
``omw-en31``; only pictograms tagged with a single synset are used, so a
"dog park" pictogram does not become a translation of *dog*.

Usage::

    uv run python scripts/prefill_animal_metaphors.py \\
        --sheet sheet.csv --wordnet omw-cmn:1.4 --out cmn.csv --extras
    uv run python scripts/prefill_animal_metaphors.py \\
        --sheet sheet.csv --arasaac ko --out ko.csv

``--sheet`` may also be a Google Sheets CSV export URL.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

import wn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metaphor_extension.wordnet_service import _hyponym_closure, load_wordnet

ANIMAL_ILI = "i35563"
PERSON_ILI = "i35562"
HOMO_ILI = "i48657"  # homo, man, human being
SENSE_ID_RE = re.compile(r"^omw-en-.+?-(\d{8}-n)$")
ASTROLOGY_RE = re.compile(r"^\(astrology\)")

# Person-domain nodes whose hyponyms are nationalities, ethnicities and
# inhabitants rather than figurative descriptions of people.  A breed named
# after a place (Afghan hound) colexifies with these without being a metaphor.
PERSON_EXCLUDE_ROOTS = {
    "i87216",  # inhabitant
    "i87232",  # national
    "i89809",  # ethnic
    "i87256",  # African
    "i87262",  # Black
    "i87277",  # White
    "i87307",  # Amerindian
    "i87496",  # Slav
    "i87520",  # Jew
    "i90774",  # Jat
    "i90935",  # Latin
}

OUTPUT_COLUMNS = [
    "English",
    "Language",
    "Checked (Y/N)",
    "Comment",
    "Person Definition",
    "Animal Definition",
    "Animal sense",
    "Person Sense",
    "Animal (wordnet)",
    "Person (wordnet)",
]


def read_sheet(source: str) -> list[dict[str, str]]:
    """Read the class sheet from a local CSV path or an export URL."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as resp:
            text = resp.read().decode("utf-8")
    else:
        text = Path(source).read_text(encoding="utf-8")
    rows = list(csv.DictReader(text.splitlines()))
    return [r for r in rows if r.get("English") and r.get("Animal sense")]


def synset_id(sense_id: str) -> str | None:
    """Turn ``omw-en-dog-02084071-n`` into ``omw-en-02084071-n``."""
    match = SENSE_ID_RE.match(sense_id.strip())
    return f"omw-en-{match.group(1)}" if match else None


def ili_of(reference: wn.Wordnet, sid: str | None) -> str | None:
    """Return the ILI of a reference synset id, or None."""
    if sid is None:
        return None
    try:
        return reference.synset(sid).ili
    except wn.Error:
        return None


def ili_lemma_index(target: wn.Wordnet) -> dict[str, list[str]]:
    """Map every ILI in the target wordnet to its lemmas (one pass)."""
    index: dict[str, list[str]] = {}
    for ss in target.synsets():
        if ss.ili and ss.pos == "n":
            index.setdefault(ss.ili, []).extend(ss.lemmas())
    return index


ARASAAC_API = "https://api.arasaac.org/api/pictograms/all/{lang}"


def fetch_arasaac(lang: str, cache_dir: Path) -> list[dict[str, Any]]:
    """Return the ARASAAC pictogram list for ``lang``, downloading once.

    Args:
        lang: ARASAAC language code (e.g. ``ko``, ``cs``, ``ja``).
        cache_dir: Directory for the cached JSON dump.

    Returns:
        The decoded API response: one dict per pictogram.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"arasaac-{lang}.json"
    if not path.exists():
        with urllib.request.urlopen(ARASAAC_API.format(lang=lang), timeout=120) as resp:
            path.write_bytes(resp.read())
    return json.loads(path.read_text(encoding="utf-8"))


def arasaac_index(
    pictograms: list[dict[str, Any]],
    reference31: wn.Wordnet,
    domains: list[set[str]] | None = None,
) -> dict[str, list[str]]:
    """Map ILIs to ARASAAC keywords.

    A pictogram tagged with several synsets is a compound ("dog park" is tagged
    park + dog) unless all its synsets belong to one domain ("cat" is tagged
    cat + house cat).  With ``domains`` given, a multi-synset pictogram is used
    only when every synset falls inside the same domain set.

    Args:
        pictograms: Output of :func:`fetch_arasaac`.
        reference31: ``omw-en31`` wordnet used to turn WordNet 3.1 offsets
            (``02086723-n``) into ILIs.
        domains: ILI sets (e.g. the animal and person closures) that make a
            multi-synset pictogram acceptable.  ``None`` accepts everything.

    Returns:
        ILI to list of distinct keywords, in the same shape as
        :func:`ili_lemma_index`.
    """
    index: dict[str, list[str]] = {}
    for pic in pictograms:
        offsets = pic.get("synsets") or []
        ilis = [ili_of(reference31, f"omw-en31-{off}") for off in offsets]
        ilis = [ili for ili in ilis if ili]
        if not ilis:
            continue
        compound = domains is not None and len(ilis) > 1
        if compound and not any(
            all(ili in domain for ili in ilis) for domain in domains
        ):
            continue
        keywords = [
            kw["keyword"].strip()
            for kw in pic.get("keywords", [])
            if kw.get("keyword", "").strip()
        ]
        for ili in ilis:
            seen = index.setdefault(ili, [])
            seen.extend(kw for kw in keywords if kw not in seen)
    return index


def merge_indexes(*indexes: dict[str, list[str]]) -> dict[str, list[str]]:
    """Union several ILI-to-lemma maps, keeping order and dropping repeats."""
    merged: dict[str, list[str]] = {}
    for index in indexes:
        for ili, lemmas in index.items():
            seen = merged.setdefault(ili, [])
            seen.extend(lemma for lemma in lemmas if lemma not in seen)
    return merged


def fill_row(
    row: dict[str, str],
    reference: wn.Wordnet,
    index: dict[str, list[str]],
) -> dict[str, str]:
    """Fill the language columns of one sheet row from the target wordnet."""
    animal_ili = ili_of(reference, synset_id(row["Animal sense"]))
    person_ili = ili_of(reference, synset_id(row["Person Sense"]))
    animal_lemmas = index.get(animal_ili or "", [])
    person_lemmas = index.get(person_ili or "", [])
    shared = [lemma for lemma in animal_lemmas if lemma in person_lemmas]

    out = {col: row.get(col, "") for col in OUTPUT_COLUMNS}
    out["Animal (wordnet)"] = "; ".join(animal_lemmas)
    out["Person (wordnet)"] = "; ".join(person_lemmas)

    if shared:
        out["Language"] = "; ".join(shared)
        out["Checked (Y/N)"] = "Y"
        out["Comment"] = "auto: wordnet has this word with both senses, please confirm"
    elif animal_lemmas:
        out["Language"] = "; ".join(animal_lemmas)
        out["Checked (Y/N)"] = ""
        out["Comment"] = (
            "auto: animal word from wordnet; person sense not recorded, please check"
        )
    else:
        out["Language"] = ""
        out["Checked (Y/N)"] = ""
        out["Comment"] = "auto: animal not in wordnet"
    return out


def domain_synsets(reference: wn.Wordnet, root_ili: str) -> dict[str, wn.Synset]:
    """Map ILI to synset for every noun under ``root_ili`` in the reference."""
    roots = reference.synsets(ili=root_ili)
    return {ss.ili: ss for ss in _hyponym_closure(roots, include_roots=False) if ss.ili}


def excluded_ilis(reference: wn.Wordnet) -> tuple[set[str], set[str]]:
    """Return (animal ILIs, person ILIs) to drop from the extras.

    Animal side: the genus Homo, everything under it (Homo sapiens, world,
    Neandertal man ...) and its taxonomic ancestors (hominid, primate,
    mammal ...), which colexify with "human" by definition, not by metaphor.
    Person side: nationalities, ethnicities and inhabitants.
    """
    homo = reference.synsets(ili=HOMO_ILI)
    animal: set[str] = {
        ss.ili for ss in _hyponym_closure(homo, include_roots=True) if ss.ili
    }
    for ss in homo:
        animal.update(x.ili for path in ss.hypernym_paths() for x in path if x.ili)
    person: set[str] = set()
    for root in PERSON_EXCLUDE_ROOTS:
        person.update(domain_synsets(reference, root))
        person.add(root)
    return animal, person


def extra_pairs(
    reference: wn.Wordnet,
    index: dict[str, list[str]],
    known: set[tuple[str, str]],
    filtered: bool = True,
) -> list[dict[str, str]]:
    """Find animal/person colexifications in the target wordnet not on the sheet.

    Hierarchy comes from the reference (English) wordnet; lemmas from the
    target.  Target lemmas sharing the same synset pair (spelling variants)
    are collapsed into one row.

    Args:
        reference: English wordnet providing the hierarchy and glosses.
        index: ILI to target-lemma map from :func:`ili_lemma_index`.
        known: (animal ILI, person ILI) pairs already on the sheet.
        filtered: drop taxonomic, nationality and astrology pairs.

    Returns:
        Sheet-shaped rows, one per (animal synset, person synset) pair.
    """
    animal_syn = domain_synsets(reference, ANIMAL_ILI)
    person_syn = domain_synsets(reference, PERSON_ILI)
    animal_skip, person_skip = excluded_ilis(reference) if filtered else (set(), set())

    lemma_animal: dict[str, set[str]] = {}
    lemma_person: dict[str, set[str]] = {}
    for ili, lemmas in index.items():
        if ili in animal_syn and ili not in animal_skip:
            for lemma in lemmas:
                lemma_animal.setdefault(lemma, set()).add(ili)
        if ili in person_syn and ili not in person_skip:
            for lemma in lemmas:
                lemma_person.setdefault(lemma, set()).add(ili)

    pairs: dict[tuple[str, str], list[str]] = {}
    for lemma in sorted(set(lemma_animal) & set(lemma_person)):
        for a_ili in lemma_animal[lemma]:
            for p_ili in lemma_person[lemma]:
                if (a_ili, p_ili) in known:
                    continue
                p_def = (person_syn[p_ili].definitions() or [""])[0]
                if filtered and ASTROLOGY_RE.match(p_def):
                    continue
                pairs.setdefault((a_ili, p_ili), []).append(lemma)

    rows: list[dict[str, str]] = []
    for (a_ili, p_ili), lemmas in sorted(pairs.items(), key=lambda kv: kv[1][0]):
        a_ss, p_ss = animal_syn[a_ili], person_syn[p_ili]
        rows.append(
            {
                "English": a_ss.lemmas()[0] if a_ss.lemmas() else a_ili,
                "Language": "; ".join(lemmas),
                "Checked (Y/N)": "Y",
                "Comment": "auto-extra: not on the English sheet; found in wordnet, please confirm",
                "Person Definition": (p_ss.definitions() or [""])[0],
                "Animal Definition": (a_ss.definitions() or [""])[0],
                "Animal sense": a_ss.id,
                "Person Sense": p_ss.id,
                "Animal (wordnet)": "; ".join(index.get(a_ili, [])),
                "Person (wordnet)": "; ".join(index.get(p_ili, [])),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--sheet", required=True, help="CSV path or Google Sheets CSV export URL."
    )
    parser.add_argument(
        "--wordnet", help="Target wordnet (e.g. omw-cmn:1.4, wnja:2.0)."
    )
    parser.add_argument(
        "--arasaac", metavar="LANG", help="Also use ARASAAC keywords for this language."
    )
    parser.add_argument(
        "--arasaac-loose",
        action="store_true",
        help="Accept multi-synset ARASAAC pictograms from any domain (noisier).",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("instance/arasaac"),
        help="Where to cache ARASAAC downloads.",
    )
    parser.add_argument(
        "--reference",
        default="omw-en:1.4",
        help="Reference wordnet for the sheet's sense ids.",
    )
    parser.add_argument(
        "--reference31",
        default="omw-en31:1.4",
        help="WordNet 3.1 lexicon used to map ARASAAC synset offsets to ILIs.",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output CSV.")
    parser.add_argument(
        "--extras", action="store_true", help="Append colexifications not on the sheet."
    )
    parser.add_argument(
        "--unfiltered",
        action="store_true",
        help="Keep taxonomic, nationality and astrology pairs in the extras.",
    )
    args = parser.parse_args(argv)
    if not args.wordnet and not args.arasaac:
        parser.error("give --wordnet, --arasaac or both")

    rows = read_sheet(args.sheet)
    reference = load_wordnet(args.reference)
    sources: list[str] = []
    indexes: list[dict[str, list[str]]] = []
    if args.wordnet:
        indexes.append(ili_lemma_index(load_wordnet(args.wordnet)))
        sources.append(args.wordnet)
    if args.arasaac:
        pictograms = fetch_arasaac(args.arasaac, args.cache_dir)
        reference31 = load_wordnet(args.reference31)
        domains = None
        if not args.arasaac_loose:
            domains = [
                set(domain_synsets(reference, ANIMAL_ILI)),
                set(domain_synsets(reference, PERSON_ILI)),
            ]
        indexes.append(arasaac_index(pictograms, reference31, domains))
        sources.append(f"arasaac:{args.arasaac}")
    index = merge_indexes(*indexes)

    filled = [fill_row(row, reference, index) for row in rows]
    summary: dict[str, int] = {"Y": 0, "animal only": 0, "missing": 0}
    for row in filled:
        if row["Checked (Y/N)"] == "Y":
            summary["Y"] += 1
        elif row["Language"]:
            summary["animal only"] += 1
        else:
            summary["missing"] += 1

    extras: list[dict[str, Any]] = []
    if args.extras:
        known = {
            (
                ili_of(reference, synset_id(r["Animal sense"])) or "",
                ili_of(reference, synset_id(r["Person Sense"])) or "",
            )
            for r in rows
        }
        extras = extra_pairs(reference, index, known, filtered=not args.unfiltered)

    with args.out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(filled)
        writer.writerows(extras)

    print(
        f"{'+'.join(sources)}: {len(filled)} sheet rows -> {summary}; "
        f"{len(extras)} extra pairs -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
