from metaphor_extension.store import AnnotationStore


def test_store_merges_existing_annotations(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.json")
    session = {
        "id": "s1",
        "items": [
            {
                "lemma": "person",
                "source_senses": [],
                "target_senses": [],
                "links": {},
                "comment": "",
                "sense_annotations": {},
                "status": "open",
            }
        ],
    }

    store.save_session(session)
    store.set_link("s1", "person", "source", "target", "metaphor")
    store.set_comment("s1", "person", "note")
    store.set_sense_annotation("s1", "person", "sense-1", "bad definition", True)
    store.set_status("s1", "person", "done")
    merged = store.save_session(session)

    item = merged["items"][0]
    assert item["links"]["source::target"]["type"] == "metaphor"
    assert item["comment"] == "note"
    assert item["sense_annotations"]["sense-1"] == {
        "comment": "bad definition",
        "bad_sense": True,
    }
    assert item["status"] == "done"


def test_empty_sense_annotation_removes_entry(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.json")
    store.save_session(
        {
            "id": "s1",
            "items": [
                {
                    "lemma": "person",
                    "source_senses": [],
                    "target_senses": [],
                    "links": {},
                    "comment": "",
                    "sense_annotations": {},
                    "status": "open",
                }
            ],
        }
    )

    store.set_sense_annotation("s1", "person", "sense-1", "bad definition", True)
    item = store.set_sense_annotation("s1", "person", "sense-1", "", False)

    assert item["sense_annotations"] == {}


def test_none_link_type_removes_link(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.json")
    store.save_session(
        {
            "id": "s1",
            "items": [
                {
                    "lemma": "person",
                    "source_senses": [],
                    "target_senses": [],
                    "links": {},
                    "comment": "",
                    "sense_annotations": {},
                    "status": "open",
                }
            ],
        }
    )

    store.set_link("s1", "person", "source", "target", "metaphor")
    item = store.set_link("s1", "person", "source", "target", "none")

    assert item["links"] == {}


def test_ignore_status_and_session_summary(tmp_path):
    store = AnnotationStore(tmp_path / "annotations.json")
    store.save_session(
        {
            "id": "s1",
            "name": "animal-human",
            "wordnet": "omw-en:1.4",
            "items": [
                {
                    "lemma": "person",
                    "source_senses": [],
                    "target_senses": [],
                    "links": {},
                    "comment": "",
                    "sense_annotations": {},
                    "status": "open",
                }
            ],
        }
    )

    store.set_status("s1", "person", "ignore")
    [summary] = store.list_sessions()

    assert summary["name"] == "animal-human"
    assert summary["counts"]["ignore"] == 1
