from metaphor_extension.app import create_app
from metaphor_extension.store import AnnotationStore


def test_unknown_session_returns_404(tmp_path):
    app = create_app({"TESTING": True, "ANNOTATION_PATH": tmp_path / "annotations.json"})
    client = app.test_client()

    response = client.get("/api/sessions/missing")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Unknown session"


def test_session_list_returns_summaries(tmp_path):
    app = create_app({"TESTING": True, "ANNOTATION_PATH": tmp_path / "annotations.json"})
    client = app.test_client()

    response = client.get("/api/sessions")

    assert response.status_code == 200
    assert response.get_json() == []


def test_sense_annotation_endpoint_updates_item(tmp_path):
    annotation_path = tmp_path / "annotations.json"
    store = AnnotationStore(annotation_path)
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
    app = create_app({"TESTING": True, "ANNOTATION_PATH": annotation_path})
    client = app.test_client()

    response = client.post(
        "/api/sessions/s1/items/person/sense",
        json={"sense_id": "sense-1", "comment": "wrong sense", "bad_sense": True},
    )

    assert response.status_code == 200
    assert response.get_json()["sense_annotations"]["sense-1"] == {
        "comment": "wrong sense",
        "bad_sense": True,
    }
