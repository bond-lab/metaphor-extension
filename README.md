# metaphor-extension
Extend chainnet to different languages top down, with a goal of comparing languages.

## Running

Install and run with `uv`:

```bash
uv run flask --app main:app run --host 127.0.0.1 --port 5001
```

Then open <http://127.0.0.1:5001>.

Run tests with:

```bash
uv run pytest
```

## Static GitHub Pages Mode

The `docs/` directory contains a browser-only version of the editor for GitHub Pages or any static file server. It cannot compute Wordnet sessions in the browser, so sessions must be precomputed first.

### Two-hierarchy intersection

Finds lemmas shared across two ILI-rooted hyponym subtrees:

```bash
uv run python scripts/build_static.py \
  --name kenet-animal-human \
  --wordnet https://raw.githubusercontent.com/StarlangSoftware/TurkishWordNet/master/kenet.xml \
  --lexicon kenet:1.0 \
  --source-ili i35563 \
  --target-ili i35562
```

### Polysemy mode

Finds lemmas in the hyponym subtree of a single ILI that are polysemous in the full wordnet. `source_senses` are the domain-anchored senses; `target_senses` are all noun senses in the wordnet so annotators can classify the relationship between each domain sense and every extended sense:

```bash
uv run python scripts/build_polysemy.py \
  --name color-en \
  --wordnet omw-en:1.4 \
  --ili i63025

uv run python scripts/build_polysemy.py \
  --name color-tr \
  --wordnet https://raw.githubusercontent.com/StarlangSoftware/TurkishWordNet/master/kenet.xml \
  --ili i63025 \
  --display-wordnet omw-en:1.4
```

Both scripts write to `docs/data/<session-name>-<session-id>.json`.

You can test it locally with:

```bash
python3 -m http.server 8000 --directory docs
```

Then open <http://127.0.0.1:8000>.

In static mode, annotations are saved in the browser's `localStorage`. Use `Export` to download a JSON annotation file and `Import` to reload one. This is suitable for GitHub Pages because no Flask server or writable filesystem is required.

The static editor does not require a session manifest. Give the generated session JSON file to an annotator; they open it in the browser, edit it, save it locally with `Save session`, and can later reopen that saved JSON.

## Annotation Workflow

The interface builds a queue of words to annotate from two ILI roots. For each word, it shows the noun senses available for that word, lets the annotator select any two senses, choose the link direction, and save a link type:

- `metaphor`
- `metonymy`
- `hypernym`
- `other`
- `none`, which removes an existing link

Links, comments, and item status are saved immediately. Item status is shown in the left queue as:

- `DONE`: finished
- `PART`: incomplete
- `IGNORE`: deliberately ignored
- `--`: not yet marked

Sessions can be named and reloaded from the stored-session selector.

## Wordnet Inputs

The target Wordnet can be supplied as:

- an installed lexicon or project id, such as `omw-en:1.4`
- a URL accepted by `wn.download()`
- a local file URL, such as `file:///path/to/wordnet.xml`

The optional `Lexicon` field can disambiguate which lexicon to use after loading a Wordnet.

## Hierarchy Approaches

### 1. Target Wordnet Hierarchy

If no reference Wordnet is provided, the app uses the target Wordnet for everything:

1. Find noun synsets for the source ILI and target ILI.
2. Traverse regular `hyponym` relations below each ILI.
3. Ignore instance/proper-name synsets.
4. Collect lemmas under each ILI.
5. Queue lemmas that occur under both ILI hierarchies.

This works best for Wordnets with a developed native hierarchy.

### 2. Reference Wordnet Hierarchy

Some Wordnets have good ILI links but little or no hierarchy. In that case, provide a reference Wordnet, normally English.

With a reference Wordnet, the app:

1. Computes the source and target hyponym closures in the reference Wordnet.
2. Extracts the descendant ILIs from those closures.
3. Looks up those ILIs in the target Wordnet.
4. Collects target-language lemmas from matching target Wordnet synsets.
5. Queues target-language lemmas that occur under both ILI sets.

So the hierarchy comes from the reference Wordnet, but the annotation queue and displayed lexical forms come from the target Wordnet.

## Filtering

The app currently restricts candidate and displayed senses to nouns.

It also filters out proper nouns represented as instance synsets:

- traversal follows `hyponym`, not `instance_hyponym`
- displayed senses with `instance_hypernym` are removed

For example, common noun senses of `wolf` remain, but person-name senses such as `Hugo Wolf` are filtered out.

## Extend Mode

Many non-English Wordnets are sparse: a target-language word may be linked to only one ILI even when the corresponding reference-language lemma has several relevant senses.

When `Extend` is enabled with a reference Wordnet, the app projects additional reference senses onto a target-language lemma when that lemma is already anchored by at least one shared ILI.

For example:

1. A Turkish lemma is linked to one ILI corresponding to English `weaver`.
2. The English reference Wordnet has additional noun synsets for `weaver` under the relevant ILI hierarchies.
3. `Extend` adds projected, clearly marked `EXTENDED` senses for the Turkish lemma from those English reference synsets.

These projected senses are not claimed to exist in the target Wordnet. They are annotation candidates derived from the reference hierarchy so annotators can handle missing target-language sense coverage explicitly.
