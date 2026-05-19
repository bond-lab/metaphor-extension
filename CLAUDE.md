# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web application for annotating semantic links (metaphor, metonymy, hypernym, other) between words shared across two ILI-rooted hyponym hierarchies in a target WordNet. Designed for cross-lingual annotation with optional reference WordNet support.

## Commands

```bash
# Run development server
uv run flask --app main:app run --host 127.0.0.1 --port 5001

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_store.py::test_save_session_merges_annotations

# Build static GitHub Pages data — two-hierarchy intersection (--display-wordnet optional)
uv run python scripts/build_static.py --name <name> --wordnet <url-or-id> \
  --source-ili <ili> --target-ili <ili> [--display-wordnet <url-or-id>]

# Build polysemy annotation data — single ILI root, polysemous words in full wordnet
uv run python scripts/build_polysemy.py --name <name> --wordnet <url-or-id> \
  --ili <ili> [--display-wordnet <url-or-id>]

# Serve static docs locally
python3 -m http.server 8000 --directory docs
```

Use `uv` (not conda) — the project ships with `pyproject.toml` and `.venv`.

## Architecture

### Core pipeline (`metaphor_extension/wordnet_service.py`)

Two session-building functions share `load_wordnet()`, `_hyponym_closure()`, and helpers:

**`build_candidate_session()`** — two-hierarchy intersection mode:
1. Loads target WordNet via `load_wordnet()`, which accepts a URL, `file://` path, project id, or lexicon id — downloading and caching via `wn` as needed
2. Computes BFS hyponym closures under source and target ILI roots (nouns only, skipping instance synsets)
3. Intersects the two sets of lemmas to produce the annotation queue
4. Optionally uses a separate reference WordNet for hierarchy (so the ILI tree comes from e.g. `omw-en:1.4` while displayed lemmas come from the target language)
5. Optionally projects additional reference senses onto target lemmas (`extend=True`) — these appear as `projected: true` in the payload and are marked `EXTENDED` in the UI

**`build_polysemy_session()`** — single-ILI polysemy mode:
1. Takes a single root ILI and collects all lemmas in its hyponym closure (including the root itself)
2. For each lemma, fetches all its noun senses in the full wordnet
3. Keeps only lemmas with 2+ total senses (polysemous in the full wordnet, not just the subtree)
4. `source_senses` = senses anchored in the subtree; `target_senses` = all senses in the wordnet
5. Annotators classify the relationship (metaphor, metonymy, etc.) between the domain sense and each extended sense

Session identity is a 16-char SHA-256 hash of all parameters; re-submitting with the same parameters returns the same session id and merges existing annotations.

### Storage (`metaphor_extension/store.py`)

`AnnotationStore` persists all sessions in a single JSON file (`instance/annotations.json`). Writes are atomic via a `.tmp` rename. `save_session()` merges new candidate items with existing annotation state (links, comments, sense\_annotations, status) keyed by lemma.

Item status values: `open`, `done`, `incomplete`, `ignore`.
Link types: `metaphor`, `metonymy`, `hypernym`, `other`, `none` (removes a link).
Link keys in storage: `"<source_sense_id>::<target_sense_id>"`.

### Flask app (`metaphor_extension/app.py`)

Created via `create_app(test_config=None)` factory. REST API:
- `POST /api/search` — build or reload a session
- `GET /api/sessions` — list session summaries with counts
- `GET /api/sessions/<id>` — full session with all items
- `POST /api/sessions/<id>/items/<lemma>/link` — set/clear a sense-pair link
- `POST /api/sessions/<id>/items/<lemma>/comment` — set comment
- `POST /api/sessions/<id>/items/<lemma>/sense` — flag a sense as bad or add a comment
- `POST /api/sessions/<id>/items/<lemma>/status` — set item status

`<lemma>` uses `<path:>` routing to allow slashes in lemma forms.

### Static mode (`scripts/build_static.py`, `scripts/build_polysemy.py`, `docs/`)

`build_static.py` calls `build_candidate_session()` and writes the result to `docs/data/<name>-<id>.json`. `build_polysemy.py` calls `build_polysemy_session()` and writes to the same directory. The `docs/` static app reads these JSON files and stores annotations in `localStorage` instead of calling a Flask server.

### Frontend (`static/`)

- `index.html` + `app.js` — Flask-backed live editor
- `session_app.js` — shared session/annotation UI logic
- `docs/index.html` + `static_app.js` — standalone static editor for GitHub Pages

## Testing Notes

Several tests in `test_wordnet_service.py` skip when specific lexicons (`omw-en:1.4`, `kenet:1.0`, `wnja:2.0`) are not installed in the local `wn` database. Install them with `wn.download("omw-en:1.4")` etc. before running the full suite.

## wn Library

**Always invoke the `wn-python` skill before writing or editing any code that uses `wn`.** The library has non-obvious gotchas around database state, lexicon scoping, and download behaviour that are documented in that skill.
