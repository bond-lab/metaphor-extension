#!/usr/bin/env python3
"""Build this year's PERSON is ANIMAL class sheet from earlier years' data.

The new sheet has the same shape as the old ones (one ``English`` master tab
plus one tab per language), with three changes:

- every metaphor the students of earlier years added is appended to the master
  list as a row of its own, with a ``Source`` column saying which tab it came
  from and what the original word was, so this year's students can check
  whether it also works in their language;
- a ``Previous`` column summarises earlier Y/N judgements (all judged tabs on
  the master tab, the same language on a language tab);
- language tabs are pre-filled with the translations earlier students of that
  language wrote, falling back to a wordnet/ARASAAC pre-fill produced by
  ``prefill_animal_metaphors.py``.  ``Checked (Y/N)`` is left blank so that
  every mark this year is a real decision.

Usage::

    uv run python scripts/build_animal_sheet.py --year 2026 \\
        --language Japanese=ja.csv="wnja 2.1" --language Czech=cs.csv="cswn 3.0" \\
        --language Slovak --language Korean=ko.csv=ARASAAC \\
        [--data data/animal-metaphors] [--out data/animal-metaphors/2026] \\
        [--reference omw-en:1.4 | --no-reference]

Each ``--language`` takes ``NAME[=PREFILL_CSV[=DESCRIPTION]]``.  The output is
one CSV per tab plus an ``.xlsx`` workbook with all tabs for import into
Google Sheets.
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from report_animal_metaphors import Row, Tab, load_year

logger = logging.getLogger(__name__)

COLUMNS = [
    "English",
    "Language",
    "Checked (Y/N)",
    "Comment",
    "Person Definition",
    "Animal Definition",
    "Animal sense",
    "Person Sense",
    "Source",
    "Previous",
    "Frequency",
]
LANGUAGES_COLUMNS = [
    "Language",
    "Investigator 1",
    "Investigator 2",
    "Investigator 3",
    "Language data from",
]
MASTER_SOURCE = "omw-en"
# English animal for free-form rows (the Polish 2024 list, one Japanese row)
# whose students gave only the word in their own language.
ENGLISH_FOR_WORD = {
    "baran": "ram",
    "bocian": "stork",
    "byczek": "bull",
    "byk": "bull",
    "gęś": "goose",
    "głupek jak kura": "hen",
    "jeleń": "stag",
    "kaczka": "duck",
    "kameleon": "chameleon",
    "koń": "horse",
    "kot": "cat",
    "kret": "mole",
    "krowa": "cow",
    "kura domowa": "hen",
    "lis": "fox",
    "małpa": "monkey",
    "myszka": "mouse",
    "niedźwiedź": "bear",
    "osioł": "donkey",
    "papuga": "parrot",
    "pies": "dog",
    "sęp": "vulture",
    "sroka": "magpie",
    "świnia": "pig",
    "wąż": "snake",
    "wilk": "wolf",
    "zając": "hare",
    "złota rybka": "goldfish",
    "żmija": "viper",
    "熊 クマ": "bear",
}
# A function from an English animal word to (sense id, definition), or None.
AnimalResolver = Callable[[str], tuple[str, str] | None]


@dataclass
class SourceEntry:
    """One tab's record of an added metaphor."""

    language: str
    year: str
    word: str
    verdict: str
    comment: str

    def __str__(self) -> str:
        text = f"{self.language} {self.year}: {self.word}".rstrip()
        if self.verdict in {"Y", "N"}:
            text += f" [{self.verdict}]"
        if self.comment:
            text += f" -- {self.comment}"
        return text


@dataclass
class Addition:
    """A metaphor added by students, merged across the tabs that listed it."""

    english: str
    meaning: str
    animal_sense: str = ""
    animal_def: str = ""
    sources: list[SourceEntry] = field(default_factory=list)

    @property
    def key(self) -> tuple[str, str]:
        """Normalised (animal, meaning) used to merge and look up additions."""
        return (normalise(self.english), normalise(self.meaning))

    @property
    def source(self) -> str:
        """Human-readable provenance, one entry per contributing tab."""
        return "; ".join(str(s) for s in self.sources)

    def from_language(self, language: str) -> SourceEntry | None:
        """The entry contributed by ``language``, if any."""
        return next((s for s in self.sources if s.language == language), None)


def normalise(text: str) -> str:
    """Lower-case and collapse whitespace and punctuation for matching."""
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def collect_additions(tabs: list[Tab]) -> list[Addition]:
    """Merge the student additions of all tabs by (animal, meaning)."""
    merged: dict[tuple[str, str], Addition] = {}
    for tab in tabs:
        for row in tab.added_rows:
            meaning = row.person_def.strip("- ").strip()
            english = row.english.strip() or row.language.strip()
            if normalise(english) == normalise(row.language):
                english = ENGLISH_FOR_WORD.get(normalise(english), english)
            if not meaning or not english:
                continue
            addition = Addition(english.lower(), meaning)
            addition = merged.setdefault(addition.key, addition)
            addition.sources.append(
                SourceEntry(
                    tab.language, tab.year, row.language, row.verdict, row.comment
                )
            )
            if row.animal_sense and not addition.animal_sense:
                addition.animal_sense = row.animal_sense
                addition.animal_def = row.animal_def
    return list(merged.values())


def previous_summary(
    tabs: list[Tab], key: tuple[str, ...], *, language: str | None = None
) -> str:
    """Summarise earlier judgements of one master pair.

    Args:
        tabs: All earlier language tabs.
        key: The pair's ``Row.key``.
        language: Restrict to this language and list each year; otherwise
            count Y and N over every judged tab.

    Returns:
        ``"Y 6, N 2"`` for the master tab, ``"2025: N; 2024: Y (default)"`` for
        a language tab, or ``""`` when nothing was recorded.
    """
    if language is None:
        counts: Counter[str] = Counter()
        for tab in tabs:
            if not tab.judged:
                continue
            for row in tab.master_rows:
                if row.key == key and row.verdict in {"Y", "N"}:
                    counts[row.verdict] += 1
        return ", ".join(f"{v} {counts[v]}" for v in ("Y", "N") if counts[v])

    parts = []
    for tab in sorted(tabs, key=lambda t: t.year, reverse=True):
        if tab.language != language:
            continue
        for row in tab.master_rows:
            if row.key != key or row.verdict == "blank":
                continue
            verdict = row.verdict
            if tab.default_y:
                verdict += " (default)"
            parts.append(f"{tab.year}: {verdict}")
    return "; ".join(parts)


def previous_translation(tabs: list[Tab], key: tuple[str, ...], language: str) -> str:
    """The most recent translation earlier students of ``language`` gave a pair."""
    for tab in sorted(tabs, key=lambda t: t.year, reverse=True):
        if tab.language != language:
            continue
        for row in tab.master_rows:
            if row.key == key and row.language.strip():
                return row.language.strip()
    return ""


def master_sheet(
    master: list[Row],
    additions: list[Addition],
    tabs: list[Tab],
    resolve: AnimalResolver | None = None,
) -> list[dict[str, str]]:
    """Build the English master tab: master pairs, then additions per animal.

    Additions for animals on the master list are placed directly after that
    animal's pairs; additions for new animals follow alphabetically.
    """
    by_animal: dict[str, list[Addition]] = defaultdict(list)
    for addition in additions:
        by_animal[normalise(addition.english)].append(addition)
    animal_rows: dict[str, Row] = {}
    for row in master:
        animal_rows.setdefault(normalise(row.english), row)

    def addition_rows(animal: str) -> list[dict[str, str]]:
        out = []
        for addition in by_animal.pop(animal, []):
            sense, definition = addition.animal_sense, addition.animal_def
            if not sense and animal in animal_rows:
                sense = animal_rows[animal].animal_sense
                definition = animal_rows[animal].animal_def
            if not sense and resolve is not None:
                resolved = resolve(addition.english)
                if resolved:
                    sense, definition = resolved
            out.append(
                {
                    **dict.fromkeys(COLUMNS, ""),
                    "English": addition.english,
                    "Person Definition": addition.meaning,
                    "Animal Definition": definition,
                    "Animal sense": sense,
                    "Source": addition.source,
                }
            )
        return out

    rows: list[dict[str, str]] = []
    done: set[str] = set()
    for row in master:
        rows.append(
            {
                **dict.fromkeys(COLUMNS, ""),
                "English": row.english,
                "Person Definition": row.person_def,
                "Animal Definition": row.animal_def,
                "Animal sense": row.animal_sense,
                "Person Sense": row.person_sense,
                "Source": MASTER_SOURCE,
                "Previous": previous_summary(tabs, row.key),
                "Frequency": row.frequency,
            }
        )
        animal = normalise(row.english)
        if animal in done:
            continue
        done.add(animal)
        last = max(i for i, r in enumerate(master) if normalise(r.english) == animal)
        if master[last] is row:
            rows += addition_rows(animal)
    for animal in sorted(by_animal):
        rows += addition_rows(animal)
    return rows


def read_prefill(path: Path | None) -> dict[tuple[str, str], dict[str, str]]:
    """Index a ``prefill_animal_metaphors.py`` CSV by (animal sense, person sense).

    The animal-only entry ``(animal sense, "")`` is also recorded so that
    additions without a person sense still get the animal word.
    """
    if path is None:
        return {}
    index: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            index[(row["Animal sense"], row["Person Sense"])] = row
            animal_word = row.get("Animal (wordnet)", "") or row.get("Language", "")
            index.setdefault(
                (row["Animal sense"], ""),
                {"Language": animal_word, "Comment": "auto: animal word from wordnet"},
            )
    return index


def language_sheet(
    master_rows: list[dict[str, str]],
    language: str,
    tabs: list[Tab],
    additions: list[Addition],
    prefill: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    """Build one language tab from the master tab, students' and pre-filled data.

    Args:
        master_rows: Output of :func:`master_sheet`.
        language: Tab name, e.g. ``Czech``.
        tabs: Earlier years' tabs (translations and judgements come from these).
        additions: Output of :func:`collect_additions`.
        prefill: Output of :func:`read_prefill`, used when students left no word.

    Returns:
        One dict per master row with ``Language``, ``Comment`` and ``Previous``
        filled in and ``Checked (Y/N)`` blank.
    """
    by_key = {a.key: a for a in additions}
    rows = []
    for base in master_rows:
        row = dict(base)
        row["Previous"] = ""
        key: tuple[str, ...] = (row["Animal sense"], row["Person Sense"])
        if row["Source"] == MASTER_SOURCE:
            row["Language"] = previous_translation(tabs, key, language)
            row["Previous"] = previous_summary(tabs, key, language=language)
        else:
            addition = by_key.get(
                (normalise(row["English"]), normalise(row["Person Definition"]))
            )
            own = addition.from_language(language) if addition else None
            if own:
                row["Language"] = own.word
                row["Previous"] = f"added by {language} {own.year} students"
        if not row["Language"]:
            hit = prefill.get(key) or prefill.get((row["Animal sense"], ""))
            if hit and hit.get("Language"):
                row["Language"] = hit["Language"]
                row["Comment"] = hit.get("Comment", "")
        rows.append(row)
    return rows


def wordnet_resolver(reference_id: str) -> AnimalResolver:
    """Resolve English animal words to a sense id and gloss in the reference wordnet.

    Args:
        reference_id: Lexicon specifier such as ``omw-en:1.4``.

    Returns:
        A function mapping a word to ``(sense_id, definition)`` of its most
        frequent synset under the animal root, or ``None`` when the word is not
        an animal.
    """
    from prefill_animal_metaphors import ANIMAL_ILI

    from metaphor_extension.wordnet_service import _hyponym_closure, load_wordnet

    reference = load_wordnet(reference_id)
    roots = reference.synsets(ili=ANIMAL_ILI)
    animals = {ss.id for ss in _hyponym_closure(roots, include_roots=False)}

    def resolve(word: str) -> tuple[str, str] | None:
        # reference.senses() keeps the lexicon's sense order, which for omw-en
        # follows WordNet's frequency ranking; take the first animal sense.
        for sense in reference.senses(word.strip(), pos="n"):
            synset = sense.synset()
            if synset.id in animals:
                definitions = synset.definitions()
                return sense.id, definitions[0] if definitions else ""
        return None

    return resolve


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    """Write rows to a CSV file with the given header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_workbook(
    path: Path, sheets: dict[str, tuple[list[str], list[dict[str, str]]]]
) -> None:
    """Write all tabs to one ``.xlsx`` workbook with a bold, frozen header row."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    book = Workbook()
    book.remove(book.active)
    for name, (columns, rows) in sheets.items():
        sheet = book.create_sheet(name)
        sheet.append(columns)
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        for row in rows:
            sheet.append([row.get(col, "") for col in columns])
        sheet.freeze_panes = "A2"
        for i, col in enumerate(columns, 1):
            width = 12 if col in {"Checked (Y/N)", "Frequency", "Previous"} else 28
            sheet.column_dimensions[get_column_letter(i)].width = width
    book.save(path)


def parse_language(spec: str) -> tuple[str, Path | None, str]:
    """Split ``NAME[=PREFILL_CSV[=DESCRIPTION]]`` into its parts."""
    parts = spec.split("=", 2) + ["", ""]
    name, prefill, description = parts[0], parts[1], parts[2]
    return name, Path(prefill) if prefill else None, description


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--year", required=True, help="Year of the new sheet.")
    parser.add_argument(
        "--language",
        action="append",
        default=[],
        metavar="NAME[=PREFILL_CSV[=DESCRIPTION]]",
        help="Language tab to create, optionally pre-filled from a CSV.",
    )
    parser.add_argument("--data", type=Path, default=Path("data/animal-metaphors"))
    parser.add_argument(
        "--out", type=Path, help="Output directory (default <data>/<year>)."
    )
    parser.add_argument("--reference", default="omw-en:1.4")
    parser.add_argument(
        "--no-reference",
        action="store_true",
        help="Do not look up sense ids for new animals in the reference wordnet.",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    out_dir = args.out or args.data / args.year

    years = sorted(p for p in args.data.iterdir() if p.is_dir() and p.name < args.year)
    if not years:
        logger.error("no earlier years under %s", args.data)
        return 1
    tabs: list[Tab] = []
    master: list[Row] = []
    for year_dir in years:
        year_master, year_tabs = load_year(year_dir)
        master = list(year_master.values())
        tabs += year_tabs

    resolve = None if args.no_reference else wordnet_resolver(args.reference)
    additions = collect_additions(tabs)
    master_rows = master_sheet(master, additions, tabs, resolve)
    sheets = {"English": (COLUMNS, master_rows)}
    languages_rows = []
    for spec in args.language:
        name, prefill_path, description = parse_language(spec)
        rows = language_sheet(
            master_rows, name, tabs, additions, read_prefill(prefill_path)
        )
        sheets[name] = (COLUMNS, rows)
        earlier = sorted({t.year for t in tabs if t.language == name})
        sources = [description] if description else []
        sources += [f"{y} students" for y in earlier]
        languages_rows.append(
            {
                **dict.fromkeys(LANGUAGES_COLUMNS, ""),
                "Language": name,
                "Language data from": ", ".join(sources),
            }
        )
        filled = sum(1 for r in rows if r["Language"])
        logger.info("%s: %d/%d rows have a translation", name, filled, len(rows))
    sheets["Languages"] = (LANGUAGES_COLUMNS, languages_rows)

    for name, (columns, rows) in sheets.items():
        write_csv(out_dir / f"{name}.csv", columns, rows)
    workbook = out_dir / f"animal-metaphors-{args.year}.xlsx"
    write_workbook(workbook, sheets)
    unresolved = sum(1 for r in master_rows if not r["Animal sense"])
    logger.info(
        "%d master pairs + %d additions (%d without a sense id) -> %s",
        len(master),
        len(additions),
        unresolved,
        workbook,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
