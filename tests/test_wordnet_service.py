import pytest
import wn

from metaphor_extension.wordnet_service import (
    _all_senses_for_form,
    _enrich_senses_with_display,
    _existing_relations,
    _merge_senses,
    _synset_payload,
    build_candidate_session,
    load_wordnet,
)


KENET_URL = "https://raw.githubusercontent.com/StarlangSoftware/TurkishWordNet/master/kenet.xml"


def has_lexicon(specifier):
    return bool(wn.lexicons(lexicon=specifier))


@pytest.mark.skipif(not has_lexicon("omw-en:1.4"), reason="omw-en:1.4 is not installed")
def test_all_senses_are_nouns_and_exclude_instances():
    wordnet = load_wordnet("omw-en:1.4")

    senses = _all_senses_for_form(wordnet, "wolf")

    assert senses
    assert {sense["synset"]["pos"] for sense in senses} == {"n"}
    assert "omw-en-wolf-01169205-v" not in {sense["id"] for sense in senses}
    assert "omw-en-Wolf-11394214-n" not in {sense["id"] for sense in senses}
    assert "omw-en-Wolf-11394398-n" not in {sense["id"] for sense in senses}


@pytest.mark.skipif(not has_lexicon("omw-en:1.4"), reason="omw-en:1.4 is not installed")
def test_existing_relations_find_direct_synset_relations():
    wordnet = load_wordnet("omw-en:1.4")
    person = wordnet.sense("omw-en-person-00007846-n")
    adult = wordnet.sense("omw-en-adult-09605289-n")
    senses = [
        {
            "id": person.id,
            "lemma": "person",
            "word_id": person.word().id,
            "synset": _synset_payload(person.synset()),
        },
        {
            "id": adult.id,
            "lemma": "adult",
            "word_id": adult.word().id,
            "synset": _synset_payload(adult.synset()),
        },
    ]

    relations = _existing_relations(senses, wordnet, wordnet)

    assert {
        "source": "omw-en-adult-09605289-n",
        "target": "omw-en-person-00007846-n",
        "source_synset": "omw-en-09605289-n",
        "target_synset": "omw-en-00007846-n",
        "type": "hypernym",
        "level": "synset",
    } in relations


@pytest.mark.skipif(not has_lexicon("kenet:1.0"), reason="kenet:1.0 is not installed")
def test_kenet_native_hierarchy_returns_overlap():
    session = build_candidate_session(KENET_URL, "i35563", "i35562", lexicon="kenet:1.0")

    assert session["lexicon"] == "kenet:1.0"
    assert session["wordnet"] == KENET_URL
    assert len(session["items"]) >= 10
    assert all(item["source_senses"] and item["target_senses"] for item in session["items"])


@pytest.mark.skipif(
    not (has_lexicon("kenet:1.0") and has_lexicon("omw-en:1.4")),
    reason="kenet:1.0 and omw-en:1.4 are not both installed",
)
def test_reference_hierarchy_uses_reference_ilis_and_target_lemmas():
    session = build_candidate_session(
        KENET_URL,
        "i35563",
        "i35562",
        lexicon="kenet:1.0",
        reference_wordnet_source="omw-en:1.4",
    )
    lemmas = {item["lemma"] for item in session["items"]}

    assert session["reference_wordnet"] == "omw-en:1.4"
    assert "insan" in lemmas
    assert "human" not in lemmas


@pytest.mark.skipif(
    not (has_lexicon("kenet:1.0") and has_lexicon("omw-en:1.4")),
    reason="kenet:1.0 and omw-en:1.4 are not both installed",
)
def test_extend_adds_projected_reference_senses():
    base = build_candidate_session(
        KENET_URL,
        "i35563",
        "i35562",
        lexicon="kenet:1.0",
        reference_wordnet_source="omw-en:1.4",
    )
    extended = build_candidate_session(
        KENET_URL,
        "i35563",
        "i35562",
        lexicon="kenet:1.0",
        reference_wordnet_source="omw-en:1.4",
        extend=True,
    )

    assert len(extended["items"]) > len(base["items"])
    assert any(
        sense.get("projected")
        for item in extended["items"]
        for sense in item["all_senses"]
    )


@pytest.mark.skipif(not has_lexicon("omw-en:1.4"), reason="omw-en:1.4 is not installed")
def test_enrich_senses_with_display_adds_display_synset():
    wordnet = load_wordnet("omw-en:1.4")
    items = [
        {
            "all_senses": [
                {
                    "id": "omw-en-person-00007846-n",
                    "synset": {"id": "omw-en-00007846-n", "ili": "i4167", "pos": "n"},
                },
                {
                    "id": "no-ili-sense",
                    "synset": {"id": "some-synset", "ili": None, "pos": "n"},
                },
            ]
        }
    ]

    _enrich_senses_with_display(items, wordnet)

    sense_with_ili = items[0]["all_senses"][0]
    sense_without_ili = items[0]["all_senses"][1]
    assert "display_synset" in sense_with_ili
    assert isinstance(sense_with_ili["display_synset"]["lemmas"], list)
    assert sense_with_ili["display_synset"]["lemmas"]
    assert "display_synset" not in sense_without_ili


def test_merge_senses_deduplicates_by_synset_id():
    senses = _merge_senses(
        [
            {
                "id": "sense-b",
                "lemma": "akanbou",
                "word_id": "word-b",
                "synset": {"id": "synset-1", "ili": "i1", "pos": "n"},
            },
            {
                "id": "sense-a",
                "lemma": "akanbou",
                "word_id": "word-a",
                "synset": {"id": "synset-1", "ili": "i1", "pos": "n"},
            },
            {
                "id": "sense-c",
                "lemma": "akanbou",
                "word_id": "word-c",
                "synset": {"id": "synset-2", "ili": "i2", "pos": "n"},
            },
        ]
    )

    assert [sense["id"] for sense in senses] == ["sense-a", "sense-c"]


@pytest.mark.skipif(not has_lexicon("wnja:2.0"), reason="wnja:2.0 is not installed")
def test_wnja_all_senses_deduplicates_duplicate_lemma_synset_senses():
    wordnet = load_wordnet("wnja:2.0")

    senses = _all_senses_for_form(wordnet, "あかんぼう")
    synset_ids = [sense["synset"]["id"] for sense in senses]

    assert len(synset_ids) == len(set(synset_ids))
