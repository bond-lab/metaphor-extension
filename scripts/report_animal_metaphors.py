#!/usr/bin/env python3
"""Analyse the PERSON is ANIMAL class sheets exported by fetch_animal_sheets.py.

Reads ``data/animal-metaphors/<year>/<Language>.csv`` and writes a Markdown
report covering:

- how much each language tab was actually worked on (Y/N judgements,
  translations, comments, added metaphors), with a flag for tabs that still
  carry the master sheet's default ``Y`` in every row;
- which English animal metaphors are shared across the most languages and
  which are rejected most often;
- year-on-year agreement for languages judged in both years;
- every metaphor the students added that is not on the English list;
- all free-text comments.

Usage::

    uv run python scripts/report_animal_metaphors.py \\
        [--data data/animal-metaphors] [--out reports/animal-metaphors.md]
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

YES = {"Y", "YES", "TRUE", "1"}
NO = {"N", "NO", "FALSE", "0"}
SKIP_TABS = {"English", "Languages"}
MIN_JUDGEMENTS = 4


@dataclass
class Row:
    """One line of a language tab."""

    english: str
    language: str
    checked: str
    comment: str
    person_def: str
    animal_def: str
    animal_sense: str
    person_sense: str
    frequency: str = ""

    @property
    def key(self) -> tuple[str, ...]:
        """Identity of a pair: the omw-en sense ids, else word plus gloss."""
        if self.animal_sense and self.person_sense:
            return (self.animal_sense, self.person_sense)
        return ("", self.english.lower(), self.person_def.lower()[:60])

    @property
    def verdict(self) -> str:
        """Normalise the Checked cell to Y, N, unsure or blank."""
        value = self.checked.strip().upper()
        if not value:
            return "blank"
        if value in YES:
            return "Y"
        if value in NO:
            return "N"
        return "unsure"


@dataclass
class Tab:
    """A language tab in one year."""

    year: str
    language: str
    rows: list[Row]
    master: dict[tuple[str, ...], Row]
    free_form: bool = False
    counts: Counter = field(default_factory=Counter)

    def __post_init__(self) -> None:
        for row in self.master_rows:
            self.counts[row.verdict] += 1

    def is_master(self, row: Row) -> bool:
        """True when the row is an unedited pair from the English master list.

        Students sometimes duplicate a row and change the person definition to
        record a different meaning; such rows keep the sense ids but count as
        added metaphors, not as judgements on the English pair.
        """
        master = self.master.get(row.key)
        if master is None:
            return False
        return (
            not master.person_def
            or not row.person_def
            or master.person_def.lower() == row.person_def.lower()
        )

    @property
    def master_rows(self) -> list[Row]:
        """Rows that correspond to a pair on the English master list."""
        return [r for r in self.rows if self.is_master(r)]

    @property
    def added_rows(self) -> list[Row]:
        """Rows the students added or re-glossed (not on the master list)."""
        return [
            r
            for r in self.rows
            if not self.is_master(r)
            and (r.english or r.language)
            and (r.person_def.strip("- ") or r.comment)
        ]

    @property
    def translated(self) -> int:
        """Master rows with something in the Language column."""
        return sum(1 for r in self.master_rows if r.language.strip())

    @property
    def comments(self) -> int:
        """Rows with a non-empty comment."""
        return sum(1 for r in self.rows if r.comment.strip())

    @property
    def default_y(self) -> bool:
        """True when every judged row is Y: probably the untouched default."""
        return (
            self.counts["Y"] > 0
            and self.counts["N"] == 0
            and self.counts["unsure"] == 0
        )

    @property
    def judged(self) -> bool:
        """True when the tab holds at least one explicit N or unsure mark."""
        return self.counts["N"] + self.counts["unsure"] > 0


def read_rows(path: Path) -> list[Row]:
    """Parse one CSV tab into rows, tolerating a blank first header cell."""
    with path.open(encoding="utf-8", newline="") as fh:
        raw = list(csv.reader(fh))
    if not raw:
        return []
    header = [h.strip() for h in raw[0]]
    if "Language" not in header or "Checked (Y/N)" not in header:
        return []  # free-form tab, handled separately
    idx = {name: header.index(name) for name in header if name}
    idx.setdefault("English", 0)

    def cell(row: list[str], name: str) -> str:
        i = idx.get(name)
        return row[i].strip() if i is not None and i < len(row) else ""

    rows = []
    for line in raw[1:]:
        if not any(c.strip() for c in line):
            continue
        rows.append(
            Row(
                english=cell(line, "English"),
                language=cell(line, "Language"),
                checked=cell(line, "Checked (Y/N)"),
                comment=cell(line, "Comment"),
                person_def=cell(line, "Person Definition"),
                animal_def=cell(line, "Animal Definition"),
                animal_sense=cell(line, "Animal sense"),
                person_sense=cell(line, "Person Sense"),
                frequency=cell(line, "Frequency"),
            )
        )
    return rows


def read_free_form(path: Path) -> list[Row]:
    """Parse a tab with its own layout (e.g. the Polish list) as added rows."""
    with path.open(encoding="utf-8", newline="") as fh:
        raw = [r for r in csv.reader(fh) if any(c.strip() for c in r)]
    rows = []
    for line in raw[1:]:
        cells = [c.strip() for c in line] + ["", "", ""]
        rows.append(
            Row(
                english=cells[1] or cells[0],
                language=cells[0],
                checked="Y",
                comment="",
                person_def=cells[2],
                animal_def="",
                animal_sense="",
                person_sense="",
            )
        )
    return rows


def load_year(year_dir: Path) -> tuple[dict[tuple[str, str], Row], list[Tab]]:
    """Load the master list and all language tabs of one year."""
    master = {r.key: r for r in read_rows(year_dir / "English.csv")}
    tabs = []
    for path in sorted(year_dir.glob("*.csv")):
        if path.stem in SKIP_TABS:
            continue
        rows = read_rows(path)
        free_form = False
        if not rows:
            rows = read_free_form(path)
            free_form = True
        tabs.append(Tab(year_dir.name, path.stem, rows, master, free_form))
    return master, tabs


def md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    """Render a Markdown table."""
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def label(row: Row) -> str:
    """Short human label for a master pair."""
    return f"**{row.english}** → {row.person_def}"


def section_tabs(tabs: list[Tab]) -> list[str]:
    """Per-tab activity table."""
    lines = ["## How much was done", ""]
    lines += [
        (
            "The English master sheet has `Y` in every row, and the language tabs were "
            "copied from it. A tab with `Y` and nothing else (*Y only*) may therefore be "
            "untouched, or its students may have used a blank for *no*; either way it "
            "is excluded from the cross-language counts below, which use only tabs with "
            "at least one explicit `N`."
        ),
        "",
    ]
    rows = []
    for t in tabs:
        if t.free_form:
            rows.append(
                [
                    t.year,
                    t.language,
                    "free-form list",
                    "",
                    "",
                    "",
                    "",
                    str(len(t.rows)),
                    "",
                ]
            )
            continue
        note = "Y only" if t.default_y else ("judged" if t.judged else "not started")
        rows.append(
            [
                t.year,
                t.language,
                note,
                str(t.counts["Y"]),
                str(t.counts["N"]),
                str(t.counts["unsure"]),
                str(t.translated),
                str(len(t.added_rows)),
                str(t.comments),
            ]
        )
    lines += md_table(
        [
            "Year",
            "Language",
            "Status",
            "Y",
            "N",
            "?",
            "Translated",
            "Added",
            "Comments",
        ],
        rows,
    )
    return lines + [""]


def section_metaphors(
    masters: dict[str, dict[tuple[str, str], Row]], tabs: list[Tab]
) -> list[str]:
    """Cross-language acceptance of each English metaphor."""
    judged = [t for t in tabs if t.judged and not t.free_form]
    votes: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(
        lambda: {"Y": [], "N": []}
    )
    for t in judged:
        for r in t.master_rows:
            if r.verdict in ("Y", "N"):
                votes[r.key][r.verdict].append(f"{t.language} {t.year}")
    master_any = {}
    for m in masters.values():
        master_any.update(m)

    scored = []
    for key, v in votes.items():
        n = len(v["Y"]) + len(v["N"])
        if n >= MIN_JUDGEMENTS and key in master_any:
            scored.append((len(v["Y"]) / n, n, key, v))

    lines = ["## Which English metaphors travel", ""]
    lines += [
        (
            f"Counted over the {len(judged)} language-years with explicit judgements "
            f"({', '.join(f'{t.language} {t.year}' for t in judged)}). "
            f"Only pairs judged in at least {MIN_JUDGEMENTS} language-years are ranked."
        ),
        "",
        "### Most widely shared",
        "",
    ]
    top = sorted(scored, key=lambda s: (-s[0], -s[1]))[:20]
    lines += md_table(
        ["Metaphor", "Y", "N", "Rejected by"],
        [
            [
                label(master_any[k]),
                str(len(v["Y"])),
                str(len(v["N"])),
                ", ".join(v["N"]),
            ]
            for _, _, k, v in top
        ],
    )
    lines += ["", "### Most often rejected", ""]
    bottom = sorted(scored, key=lambda s: (s[0], -s[1]))[:20]
    lines += md_table(
        ["Metaphor", "Y", "N", "Accepted by"],
        [
            [
                label(master_any[k]),
                str(len(v["Y"])),
                str(len(v["N"])),
                ", ".join(v["Y"]),
            ]
            for _, _, k, v in bottom
        ],
    )
    lines += ["", "### Acceptance by animal", ""]
    by_animal: dict[str, Counter] = defaultdict(Counter)
    for key, v in votes.items():
        if key in master_any:
            by_animal[master_any[key].english]["Y"] += len(v["Y"])
            by_animal[master_any[key].english]["N"] += len(v["N"])
    animal_rows = sorted(
        by_animal.items(),
        key=lambda kv: -(kv[1]["Y"] / max(1, kv[1]["Y"] + kv[1]["N"])),
    )
    lines += md_table(
        ["Animal", "Y", "N", "Share Y"],
        [
            [a, str(c["Y"]), str(c["N"]), f"{c['Y'] / (c['Y'] + c['N']):.0%}"]
            for a, c in animal_rows
            if c["Y"] + c["N"] >= MIN_JUDGEMENTS
        ],
    )
    return lines + [""]


def section_years(
    tabs: list[Tab], masters: dict[str, dict[tuple[str, str], Row]]
) -> list[str]:
    """Agreement between years for languages judged twice."""
    lines = ["## Year-on-year agreement", ""]
    by_lang: dict[str, dict[str, Tab]] = defaultdict(dict)
    for t in tabs:
        if t.judged and not t.free_form:
            by_lang[t.language][t.year] = t
    master_any = {}
    for m in masters.values():
        master_any.update(m)
    any_pair = False
    for lang, years in sorted(by_lang.items()):
        if len(years) < 2:
            continue
        any_pair = True
        (y1, t1), (y2, t2) = sorted(years.items())
        v1 = {r.key: r.verdict for r in t1.master_rows if r.verdict in ("Y", "N")}
        v2 = {r.key: r.verdict for r in t2.master_rows if r.verdict in ("Y", "N")}
        both = sorted(set(v1) & set(v2))
        agree = [k for k in both if v1[k] == v2[k]]
        lines += [f"### {lang}: {y1} vs {y2}", ""]
        lines.append(
            f"{len(both)} pairs judged in both years, {len(agree)} agree "
            f"({len(agree) / len(both):.0%})."
            if both
            else "No pair judged in both years."
        )
        disagreements = [k for k in both if v1[k] != v2[k]]
        if disagreements:
            lines += ["", "Disagreements:", ""]
            lines += md_table(
                ["Metaphor", y1, y2],
                [
                    [label(master_any[k]), v1[k], v2[k]]
                    for k in disagreements
                    if k in master_any
                ],
            )
        lines.append("")
    if not any_pair:
        lines += ["No language has explicit judgements in both years.", ""]
    return lines


def section_added(tabs: list[Tab]) -> list[str]:
    """Metaphors the students added."""
    lines = ["## Metaphors added by students", ""]
    for t in tabs:
        added = t.added_rows
        if not added:
            continue
        lines += [f"### {t.language} {t.year} ({len(added)})", ""]
        lines += md_table(
            ["Word", "English", "Meaning", "Y/N", "Comment"],
            [
                [
                    r.language,
                    r.english,
                    r.person_def or r.animal_def,
                    r.verdict if r.verdict != "blank" else "",
                    r.comment,
                ]
                for r in added
            ],
        )
        lines.append("")
    return lines


def section_comments(tabs: list[Tab]) -> list[str]:
    """All free-text comments."""
    lines = ["## Comments", ""]
    for t in tabs:
        commented = [r for r in t.rows if r.comment.strip()]
        if not commented:
            continue
        lines += [f"### {t.language} {t.year}", ""]
        for r in commented:
            where = f"{r.english} ({r.language})" if r.language else r.english
            lines.append(f"- **{where}** [{r.verdict}]: {r.comment}")
        lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--data", type=Path, default=Path("data/animal-metaphors"))
    parser.add_argument("--out", type=Path, default=Path("reports/animal-metaphors.md"))
    args = parser.parse_args(argv)

    masters: dict[str, dict[tuple[str, str], Row]] = {}
    tabs: list[Tab] = []
    for year_dir in sorted(p for p in args.data.iterdir() if p.is_dir()):
        master, year_tabs = load_year(year_dir)
        if not any(t.judged for t in year_tabs):
            print(f"{year_dir.name}: no judgements yet, skipped")
            continue
        masters[year_dir.name] = master
        tabs += year_tabs

    lines = [
        "# PERSON is ANIMAL metaphors across languages: class data "
        + " and ".join(masters),
        "",
    ]
    lines.append(
        "Source: student-filled Google Sheets, one tab per language, each row an English "
        "animal→person sense pair from omw-en marked Y (the metaphor works in the language) "
        "or N. Generated by `scripts/report_animal_metaphors.py`."
    )
    lines.append("")
    lines += section_tabs(tabs)
    lines += section_metaphors(masters, tabs)
    lines += section_years(tabs, masters)
    lines += section_added(tabs)
    lines += section_comments(tabs)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(tabs)} tabs -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
