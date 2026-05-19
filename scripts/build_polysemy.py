from __future__ import annotations

import argparse
import json
from pathlib import Path

from metaphor_extension.wordnet_service import build_polysemy_session

KENET_URL = "https://raw.githubusercontent.com/StarlangSoftware/TurkishWordNet/master/kenet.xml"


def safe_filename(value: str) -> str:
    """Sanitize a session name for use in a filename."""
    filename = "".join(char if char.isalnum() or char in "._-" else "_" for char in str(value))
    filename = filename.strip("_")
    return filename or "session"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build static polysemy annotation data from a single ILI root concept."
    )
    parser.add_argument("--out", default="docs/data", help="Output data directory.")
    parser.add_argument("--name", required=True, help="Session name.")
    parser.add_argument("--wordnet", default=KENET_URL, help="Target Wordnet (URL, path, or id).")
    parser.add_argument("--lexicon", default=None, help="Optional target lexicon specifier.")
    parser.add_argument("--ili", required=True, help="Root ILI concept (e.g. i113545).")
    parser.add_argument("--display-wordnet", default="", help="Optional display Wordnet for labels.")
    parser.add_argument("--display-lexicon", default=None, help="Optional display lexicon specifier.")
    args = parser.parse_args()

    if args.lexicon is None and args.wordnet == KENET_URL:
        args.lexicon = "kenet:1.0"

    session = build_polysemy_session(
        args.wordnet,
        args.ili,
        args.lexicon,
        args.name,
        args.display_wordnet or None,
        args.display_lexicon,
    )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    session_path = out / f"{safe_filename(session['name'])}-{session['id']}.json"
    session_path.write_text(
        json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {session_path} ({len(session['items'])} items)")


if __name__ == "__main__":
    main()
