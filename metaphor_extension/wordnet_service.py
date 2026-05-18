from __future__ import annotations

import hashlib
import json
import urllib.parse
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import wn


LINK_TYPES = {"metaphor", "metonymy", "hypernym", "other"}
EMPTY_LINK_TYPE = "none"


@dataclass(frozen=True)
class SessionKey:
    name: str
    wordnet: str
    lexicon: str | None
    reference_wordnet: str | None
    reference_lexicon: str | None
    extend: bool
    source_ili: str
    target_ili: str
    # display_wordnet is excluded from the id hash: display is a view preference,
    # not part of the annotation identity.

    @property
    def id(self) -> str:
        raw = json.dumps(
            {
                "name": self.name,
                "wordnet": self.wordnet,
                "lexicon": self.lexicon,
                "reference_wordnet": self.reference_wordnet,
                "reference_lexicon": self.reference_lexicon,
                "extend": self.extend,
                "source_ili": self.source_ili,
                "target_ili": self.target_ili,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class WordnetError(ValueError):
    pass


def load_wordnet(source: str, lexicon: str | None = None) -> wn.Wordnet:
    source = (source or "").strip()
    if lexicon:
        try:
            return wn.Wordnet(lexicon)
        except wn.Error:
            if not source:
                raise

    if not source:
        raise WordnetError("Provide a Wordnet URL, file:// path, project id, or lexicon id.")

    before = {lex.specifier() for lex in wn.lexicons()}
    plain_path = Path(source).expanduser()
    if plain_path.exists():
        wn.add(plain_path)
    elif source.startswith("file://"):
        parsed = urllib.parse.urlparse(source)
        path = Path(urllib.parse.unquote(parsed.path)).expanduser()
        if not path.exists():
            raise WordnetError(f"Wordnet file does not exist: {path}")
        wn.add(path)
    elif "://" in source:
        wn.download(source, add=True)
    else:
        try:
            return wn.Wordnet(source)
        except wn.Error:
            wn.download(source, add=True)

    after = {lex.specifier(): lex for lex in wn.lexicons()}
    added = [specifier for specifier in after if specifier not in before]
    chosen = added[0] if len(added) == 1 else _guess_lexicon(source, after)
    if not chosen:
        raise WordnetError(
            "Loaded the Wordnet, but could not infer which lexicon to use. "
            "Submit the lexicon field explicitly, e.g. omw-en:1.4."
        )
    return wn.Wordnet(chosen)


def _guess_lexicon(source: str, lexicons: dict[str, wn.Lexicon]) -> str | None:
    low = source.lower()
    matches = [
        spec
        for spec, lex in lexicons.items()
        if spec.lower() in low or lex.id.lower() in low or (lex.label or "").lower() in low
    ]
    return matches[0] if len(matches) == 1 else None


def _enrich_senses_with_display(items: list[dict[str, Any]], display_wordnet: wn.Wordnet) -> None:
    """Add display_synset to each sense via ILI lookup in the display wordnet."""
    for item in items:
        for sense in item.get("all_senses", []):
            ili = sense.get("synset", {}).get("ili")
            if not ili:
                continue
            for ref_synset in display_wordnet.synsets(ili=ili):
                if ref_synset.pos == "n" and not _is_instance_synset(ref_synset):
                    sense["display_synset"] = {
                        "lemmas": ref_synset.lemmas(),
                        "definition": ref_synset.definition() or "",
                    }
                    break


def build_candidate_session(
    wordnet_source: str,
    source_ili: str,
    target_ili: str,
    lexicon: str | None = None,
    name: str | None = None,
    reference_wordnet_source: str | None = None,
    reference_lexicon: str | None = None,
    extend: bool = False,
    display_wordnet_source: str | None = None,
    display_lexicon: str | None = None,
) -> dict[str, Any]:
    session_name = (name or "").strip() or f"{source_ili} / {target_ili}"
    reference_wordnet_source = (reference_wordnet_source or "").strip() or None
    key = SessionKey(
        session_name,
        wordnet_source,
        lexicon,
        reference_wordnet_source,
        reference_lexicon,
        extend,
        source_ili,
        target_ili,
    )
    wordnet = load_wordnet(wordnet_source, lexicon)
    hierarchy_wordnet = (
        load_wordnet(reference_wordnet_source, reference_lexicon)
        if reference_wordnet_source
        else wordnet
    )
    source_roots = [synset for synset in hierarchy_wordnet.synsets(ili=source_ili) if synset.pos == "n"]
    target_roots = [synset for synset in hierarchy_wordnet.synsets(ili=target_ili) if synset.pos == "n"]
    if not source_roots:
        raise WordnetError(f"No noun synsets found for source ILI {source_ili}.")
    if not target_roots:
        raise WordnetError(f"No noun synsets found for target ILI {target_ili}.")

    source_ilis = {synset.ili for synset in _hyponym_closure(source_roots, include_roots=False) if synset.ili}
    target_ilis = {synset.ili for synset in _hyponym_closure(target_roots, include_roots=False) if synset.ili}
    if reference_wordnet_source:
        source = _lemmas_for_ilis(wordnet, source_ilis)
        target = _lemmas_for_ilis(wordnet, target_ilis)
        reference_source = _lemmas_under(source_roots, include_roots=False)
        reference_target = _lemmas_under(target_roots, include_roots=False)
        if extend:
            _extend_from_reference(wordnet, hierarchy_wordnet, source, target, reference_source, reference_target)
    else:
        source = _lemmas_under(source_roots, include_roots=False)
        target = _lemmas_under(target_roots, include_roots=False)
    lemmas = sorted(set(source) & set(target), key=lambda item: item.casefold())
    items = []
    for lemma in lemmas:
        all_senses = _merge_senses(_all_senses_for_form(wordnet, lemma), source[lemma], target[lemma])
        items.append(
            {
                "lemma": lemma,
                "all_senses": all_senses,
                "source_senses": source[lemma],
                "target_senses": target[lemma],
                "links": {},
                "existing_relations": _existing_relations(all_senses, wordnet, hierarchy_wordnet),
                "comment": "",
                "sense_annotations": {},
                "status": "open",
            }
        )

    display_wn_source = (display_wordnet_source or "").strip() or None
    display_wn: wn.Wordnet | None = None
    if display_wn_source:
        display_wn = load_wordnet(display_wn_source, display_lexicon)
    elif reference_wordnet_source:
        display_wn = hierarchy_wordnet

    if display_wn is not None:
        _enrich_senses_with_display(items, display_wn)

    resolved_display_lexicon: str | None = None
    if display_wn is not None:
        lexicons = display_wn.lexicons()
        if len(lexicons) == 1:
            resolved_display_lexicon = lexicons[0].specifier()
        else:
            resolved_display_lexicon = display_lexicon

    return {
        "id": key.id,
        "name": session_name,
        "wordnet": wordnet_source,
        "lexicon": wordnet.lexicons()[0].specifier() if len(wordnet.lexicons()) == 1 else lexicon,
        "reference_wordnet": reference_wordnet_source,
        "reference_lexicon": (
            hierarchy_wordnet.lexicons()[0].specifier()
            if reference_wordnet_source and len(hierarchy_wordnet.lexicons()) == 1
            else reference_lexicon
        ),
        "display_wordnet": display_wn_source or (reference_wordnet_source if display_wn else None),
        "display_lexicon": resolved_display_lexicon,
        "extend": extend,
        "source_ili": source_ili,
        "target_ili": target_ili,
        "source_roots": [_synset_payload(synset) for synset in source_roots],
        "target_roots": [_synset_payload(synset) for synset in target_roots],
        "items": items,
    }


def _lemmas_for_ilis(wordnet: wn.Wordnet, ilis: set[str]) -> dict[str, list[dict[str, Any]]]:
    by_lemma: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for ili in sorted(ilis):
        for synset in wordnet.synsets(ili=ili):
            if synset.pos != "n" or _is_instance_synset(synset):
                continue
            payload = _synset_payload(synset)
            for sense in synset.senses():
                word = sense.word()
                for form in word.forms() or [word.lemma()]:
                    _add_sense(
                        by_lemma[form],
                        {
                            "id": sense.id,
                            "lemma": form,
                            "word_id": word.id,
                            "synset": payload,
                        },
                    )
    return {
        lemma: sorted(senses.values(), key=lambda sense: sense["id"])
        for lemma, senses in by_lemma.items()
    }


def _lemmas_under(roots: list[wn.Synset], *, include_roots: bool) -> dict[str, list[dict[str, Any]]]:
    by_lemma: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for synset in _hyponym_closure(roots, include_roots=include_roots):
        payload = _synset_payload(synset)
        for sense in synset.senses():
            word = sense.word()
            forms = word.forms() or [word.lemma()]
            for form in forms:
                _add_sense(
                    by_lemma[form],
                    {
                        "id": sense.id,
                        "lemma": form,
                        "word_id": word.id,
                        "synset": payload,
                    },
                )
    return {
        lemma: sorted(senses.values(), key=lambda sense: sense["id"])
        for lemma, senses in by_lemma.items()
    }


def _all_senses_for_form(wordnet: wn.Wordnet, form: str) -> list[dict[str, Any]]:
    senses = {}
    for sense in wordnet.senses(form, pos="n"):
        word = sense.word()
        synset = sense.synset()
        if _is_instance_synset(synset):
            continue
        _add_sense(
            senses,
            {
                "id": sense.id,
                "lemma": form,
                "word_id": word.id,
                "synset": _synset_payload(synset),
            },
        )
    return sorted(senses.values(), key=lambda sense: sense["id"])


def _extend_from_reference(
    wordnet: wn.Wordnet,
    reference_wordnet: wn.Wordnet,
    source: dict[str, list[dict[str, Any]]],
    target: dict[str, list[dict[str, Any]]],
    reference_source: dict[str, list[dict[str, Any]]],
    reference_target: dict[str, list[dict[str, Any]]],
) -> None:
    for lemma in sorted(set(source) | set(target)):
        reference_lemmas = _reference_lemmas_anchored_by_target_senses(
            reference_wordnet,
            [*source.get(lemma, []), *target.get(lemma, [])],
        )
        for reference_lemma in reference_lemmas:
            if reference_lemma in reference_source:
                source.setdefault(lemma, [])
                source[lemma] = _merge_senses(
                    source[lemma],
                    _project_reference_senses(lemma, reference_lemma, reference_source[reference_lemma]),
                )
            if reference_lemma in reference_target:
                target.setdefault(lemma, [])
                target[lemma] = _merge_senses(
                    target[lemma],
                    _project_reference_senses(lemma, reference_lemma, reference_target[reference_lemma]),
                )


def _reference_lemmas_anchored_by_target_senses(
    reference_wordnet: wn.Wordnet,
    target_senses: list[dict[str, Any]],
) -> set[str]:
    lemmas = set()
    for target_sense in target_senses:
        ili = target_sense["synset"].get("ili")
        if not ili:
            continue
        for reference_synset in reference_wordnet.synsets(ili=ili):
            if reference_synset.pos != "n" or _is_instance_synset(reference_synset):
                continue
            for reference_lemma in reference_synset.lemmas():
                lemmas.add(reference_lemma)
    return lemmas


def _project_reference_senses(
    target_lemma: str,
    reference_lemma: str,
    reference_senses: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    projected = []
    for sense in reference_senses:
        projected.append(
            {
                "id": f"projected:{target_lemma}:{sense['id']}",
                "lemma": target_lemma,
                "word_id": f"projected:{target_lemma}",
                "projected": True,
                "reference_lemma": reference_lemma,
                "reference_sense_id": sense["id"],
                "synset": {
                    **sense["synset"],
                    "lemmas": [target_lemma, *sense["synset"].get("lemmas", [])],
                    "projected": True,
                },
            }
        )
    return projected


def _merge_senses(*sense_lists: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {}
    for senses in sense_lists:
        for sense in senses:
            _add_sense(merged, sense)
    return sorted(merged.values(), key=lambda sense: sense["id"])


def _existing_relations(
    senses: list[dict[str, Any]],
    wordnet: wn.Wordnet,
    hierarchy_wordnet: wn.Wordnet,
) -> list[dict[str, Any]]:
    by_sense_id = {sense["id"]: sense for sense in senses}
    by_synset_id = {sense["synset"]["id"]: sense for sense in senses if sense.get("synset", {}).get("id")}
    by_ili: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sense in senses:
        ili = sense.get("synset", {}).get("ili")
        if ili:
            by_ili[ili].append(sense)
    relations = {}
    for sense in senses:
        synset_id = sense.get("synset", {}).get("id")
        if not synset_id:
            continue
        for current_wordnet in _unique_wordnets(wordnet, hierarchy_wordnet):
            synset = _get_synset(current_wordnet, synset_id)
            if synset:
                _add_existing_synset_relations(relations, sense, synset, by_synset_id)
            current_sense = _get_sense(current_wordnet, sense["id"])
            if current_sense:
                _add_existing_sense_relations(relations, sense, current_sense, by_sense_id, by_synset_id)
        _add_existing_reference_ili_relations(relations, sense, hierarchy_wordnet, by_ili)
    return sorted(
        relations.values(),
        key=lambda relation: (
            relation["source"],
            relation["target"],
            relation["level"],
            relation["type"],
        ),
    )


def _add_existing_synset_relations(
    relations: dict[str, dict[str, Any]],
    source_sense: dict[str, Any],
    source_synset: wn.Synset,
    by_synset_id: dict[str, dict[str, Any]],
) -> None:
    for relation_type, targets in source_synset.relations().items():
        for target_synset in targets:
            target_sense = by_synset_id.get(target_synset.id)
            if not target_sense or target_sense["id"] == source_sense["id"]:
                continue
            relation = {
                "source": source_sense["id"],
                "target": target_sense["id"],
                "source_synset": source_synset.id,
                "target_synset": target_synset.id,
                "type": relation_type,
                "level": "synset",
            }
            relations[_existing_relation_key(relation)] = relation


def _add_existing_sense_relations(
    relations: dict[str, dict[str, Any]],
    source_sense: dict[str, Any],
    current_sense: wn.Sense,
    by_sense_id: dict[str, dict[str, Any]],
    by_synset_id: dict[str, dict[str, Any]],
) -> None:
    for relation_type, targets in current_sense.relations().items():
        for target in targets:
            target_sense = by_sense_id.get(target.id) or by_synset_id.get(target.synset().id)
            if not target_sense or target_sense["id"] == source_sense["id"]:
                continue
            relation = {
                "source": source_sense["id"],
                "target": target_sense["id"],
                "source_synset": source_sense["synset"]["id"],
                "target_synset": target_sense["synset"]["id"],
                "type": relation_type,
                "level": "sense",
            }
            relations[_existing_relation_key(relation)] = relation


def _add_existing_reference_ili_relations(
    relations: dict[str, dict[str, Any]],
    source_sense: dict[str, Any],
    reference_wordnet: wn.Wordnet,
    by_ili: dict[str, list[dict[str, Any]]],
) -> None:
    source_ili = source_sense.get("synset", {}).get("ili")
    if not source_ili:
        return
    for source_synset in reference_wordnet.synsets(ili=source_ili):
        for relation_type, targets in source_synset.relations().items():
            for target_synset in targets:
                target_ili = target_synset.ili
                for target_sense in by_ili.get(target_ili, []):
                    if target_sense["id"] == source_sense["id"]:
                        continue
                    relation = {
                        "source": source_sense["id"],
                        "target": target_sense["id"],
                        "source_synset": source_sense["synset"]["id"],
                        "target_synset": target_sense["synset"]["id"],
                        "source_reference_synset": source_synset.id,
                        "target_reference_synset": target_synset.id,
                        "type": relation_type,
                        "level": "reference",
                    }
                    relations[_existing_relation_key(relation)] = relation


def _existing_relation_key(relation: dict[str, Any]) -> str:
    return "::".join(
        [
            relation["source"],
            relation["target"],
            relation["level"],
            relation["type"],
        ]
    )


def _unique_wordnets(*wordnets: wn.Wordnet) -> list[wn.Wordnet]:
    unique = []
    seen = set()
    for wordnet in wordnets:
        key = tuple(lex.specifier() for lex in wordnet.lexicons())
        if key in seen:
            continue
        seen.add(key)
        unique.append(wordnet)
    return unique


def _get_synset(wordnet: wn.Wordnet, synset_id: str) -> wn.Synset | None:
    try:
        return wordnet.synset(synset_id)
    except wn.Error:
        return None


def _get_sense(wordnet: wn.Wordnet, sense_id: str) -> wn.Sense | None:
    try:
        return wordnet.sense(sense_id)
    except wn.Error:
        return None


def _add_sense(senses: dict[str, dict[str, Any]], sense: dict[str, Any]) -> None:
    key = _sense_merge_key(sense)
    existing = senses.get(key)
    if existing is None or sense["id"] < existing["id"]:
        senses[key] = sense


def _sense_merge_key(sense: dict[str, Any]) -> str:
    synset_id = sense.get("synset", {}).get("id")
    return f"synset:{synset_id}" if synset_id else f"sense:{sense['id']}"


def _hyponym_closure(roots: list[wn.Synset], *, include_roots: bool) -> list[wn.Synset]:
    seen: set[str] = set()
    result: list[wn.Synset] = []
    queue = deque((root, 0) for root in roots)
    while queue:
        synset, depth = queue.popleft()
        if synset.id in seen:
            continue
        seen.add(synset.id)
        if synset.pos != "n" or _is_instance_synset(synset):
            continue
        if include_roots or depth > 0:
            result.append(synset)
        children = synset.relations().get("hyponym", [])
        for child in children:
            queue.append((child, depth + 1))
    return result


def _is_instance_synset(synset: wn.Synset) -> bool:
    return bool(synset.relations().get("instance_hypernym"))


def _synset_payload(synset: wn.Synset) -> dict[str, Any]:
    return {
        "id": synset.id,
        "ili": synset.ili,
        "pos": synset.pos,
        "lemmas": synset.lemmas(),
        "definition": synset.definition() or "",
    }
