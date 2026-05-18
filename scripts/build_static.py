from __future__ import annotations

import argparse
import json
from pathlib import Path

from metaphor_extension.wordnet_service import build_candidate_session

KENET_URL = "https://raw.githubusercontent.com/StarlangSoftware/TurkishWordNet/master/kenet.xml"


def build_static_session(args: argparse.Namespace) -> dict:
    session = build_candidate_session(
        args.wordnet,
        args.source_ili,
        args.target_ili,
        args.lexicon,
        args.name,
        args.reference_wordnet or None,
        args.reference_lexicon,
        args.extend,
        args.display_wordnet or None,
        args.display_lexicon,
    )
    return write_static_session(session, Path(args.out))


def write_static_session(session: dict, out: Path) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    session_path = out / f"{safe_filename(session.get('name') or 'session')}-{session['id']}.json"
    session_path.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"session_path": session_path}


def safe_filename(value: str) -> str:
    filename = "".join(char if char.isalnum() or char in "._-" else "_" for char in str(value))
    filename = filename.strip("_")
    return filename or "session"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static GitHub Pages annotation data.")
    parser.add_argument("--out", default="docs/data", help="Output data directory.")
    parser.add_argument("--name", default="animal-human", help="Session name.")
    parser.add_argument("--wordnet", default=KENET_URL, help="Target Wordnet.")
    parser.add_argument("--lexicon", default=None, help="Optional target lexicon.")
    parser.add_argument("--source-ili", default="i35563", help="Source ILI.")
    parser.add_argument("--target-ili", default="i35562", help="Target ILI.")
    parser.add_argument("--reference-wordnet", default="", help="Optional reference Wordnet.")
    parser.add_argument("--reference-lexicon", default=None, help="Optional reference lexicon.")
    parser.add_argument("--extend", action="store_true", help="Project missing senses from the reference Wordnet.")
    parser.add_argument("--display-wordnet", default="", help="Optional second-language display Wordnet.")
    parser.add_argument("--display-lexicon", default=None, help="Optional display lexicon.")
    args = parser.parse_args()
    if args.lexicon is None and args.wordnet == KENET_URL:
        args.lexicon = "kenet:1.0"

    result = build_static_session(args)
    print(f"Wrote {result['session_path']} ({len(json.loads(result['session_path'].read_text(encoding='utf-8'))['items'])} items)")


if __name__ == "__main__":
    main()
