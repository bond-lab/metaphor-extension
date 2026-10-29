#!/usr/bin/env python3
"""Export every tab of the PERSON is ANIMAL class Google Sheets to CSV.

Writes ``data/animal-metaphors/<year>/<Tab>.csv`` for each tab of each sheet in
``SHEETS`` and regenerates ``data/animal-metaphors/README.md``.  Tab names and
ids are read from the sheet's public ``htmlview`` page, so the sheets must be
shared as "anyone with the link can view".

Usage::

    uv run python scripts/fetch_animal_sheets.py
"""

from __future__ import annotations

import datetime
import html
import re
import urllib.request
from pathlib import Path

SHEETS = {
    "2024": "1-DzF1WtoDigSmRFe1PbrM7r-4x5ivolPr5TyXanePqw",
    "2025": "1K9_pb-uuqVQTmALSTz4AGy5ZaTYHqd3TlG2ADk-f890",
}
OUT_ROOT = Path("data/animal-metaphors")
TAB_RE = re.compile(r'items\.push\(\{name: "([^"]+)", pageUrl: "[^"]*?gid=(\d+)')


def fetch(url: str) -> bytes:
    """Return the body of ``url`` with a browser user agent."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def tabs(sheet_id: str) -> list[tuple[str, str]]:
    """Return (tab name, gid) pairs for a public sheet."""
    page = fetch(f"https://docs.google.com/spreadsheets/d/{sheet_id}/htmlview")
    text = html.unescape(page.decode("utf-8", errors="replace")).replace("\\/", "/")
    return TAB_RE.findall(text)


def safe_name(name: str) -> str:
    """Turn a tab name into a filename stem."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip()).strip("_")


def main() -> int:
    """Download all tabs and write the README index."""
    today = datetime.date.today().isoformat()
    lines = [
        "# PERSON is ANIMAL class data",
        "",
        "Raw exports of the Google Sheets used in the *Linguistics of Asian Languages*",
        "metaphor week. One CSV per sheet tab; the `English` tab is the master list of",
        "English animal/person sense pairs that students translate and mark Y/N.",
        f"Downloaded {today} with `scripts/fetch_animal_sheets.py`.",
        "",
    ]
    for year, sheet_id in SHEETS.items():
        out_dir = OUT_ROOT / year
        out_dir.mkdir(parents=True, exist_ok=True)
        lines += [
            f"## {year}",
            "",
            f"Source: https://docs.google.com/spreadsheets/d/{sheet_id}/",
            "",
            "| Tab | File |",
            "|---|---|",
        ]
        for name, gid in tabs(sheet_id):
            stem = safe_name(name) or f"gid{gid}"
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
            (out_dir / f"{stem}.csv").write_bytes(fetch(url))
            lines.append(f"| {name} (gid {gid}) | `{year}/{stem}.csv` |")
            print(f"{year}/{stem}.csv")
        lines.append("")
    (OUT_ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
