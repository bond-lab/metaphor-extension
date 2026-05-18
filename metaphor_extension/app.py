from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .store import AnnotationStore
from .wordnet_service import WordnetError, build_candidate_session


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder="../static", static_url_path="")
    app.config.update(
        ANNOTATION_PATH=Path(app.instance_path) / "annotations.json",
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    store = AnnotationStore(Path(app.config["ANNOTATION_PATH"]))

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.post("/api/search")
    def search():
        payload = request.get_json(force=True)
        try:
            session = build_candidate_session(
                payload.get("wordnet", ""),
                payload.get("source_ili", ""),
                payload.get("target_ili", ""),
                payload.get("lexicon") or None,
                payload.get("name") or None,
                payload.get("reference_wordnet") or None,
                payload.get("reference_lexicon") or None,
                bool(payload.get("extend")),
                payload.get("display_wordnet") or None,
                payload.get("display_lexicon") or None,
            )
            session = store.save_session(session)
        except (WordnetError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(session)

    @app.get("/api/sessions")
    def list_sessions():
        return jsonify(store.list_sessions())

    @app.get("/api/sessions/<session_id>")
    def get_session(session_id: str):
        session = store.get(session_id)
        if not session:
            return jsonify({"error": "Unknown session"}), 404
        return jsonify(session)

    @app.post("/api/sessions/<session_id>/items/<path:lemma>/link")
    def set_link(session_id: str, lemma: str):
        payload = request.get_json(force=True)
        try:
            item = store.set_link(
                session_id,
                lemma,
                payload["source"],
                payload["target"],
                payload["type"],
            )
        except (KeyError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(item)

    @app.post("/api/sessions/<session_id>/items/<path:lemma>/comment")
    def set_comment(session_id: str, lemma: str):
        payload = request.get_json(force=True)
        try:
            item = store.set_comment(session_id, lemma, payload.get("comment", ""))
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(item)

    @app.post("/api/sessions/<session_id>/items/<path:lemma>/sense")
    def set_sense_annotation(session_id: str, lemma: str):
        payload = request.get_json(force=True)
        try:
            item = store.set_sense_annotation(
                session_id,
                lemma,
                payload["sense_id"],
                payload.get("comment", ""),
                bool(payload.get("bad_sense", False)),
            )
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(item)

    @app.post("/api/sessions/<session_id>/items/<path:lemma>/status")
    def set_status(session_id: str, lemma: str):
        payload = request.get_json(force=True)
        try:
            item = store.set_status(session_id, lemma, payload.get("status", "open"))
        except (KeyError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(item)

    return app
