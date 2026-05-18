import json
import importlib.util
import argparse
from pathlib import Path

BUILD_STATIC_PATH = Path(__file__).parents[1] / "scripts" / "build_static.py"
spec = importlib.util.spec_from_file_location("build_static", BUILD_STATIC_PATH)
build_static = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_static)
KENET_URL = build_static.KENET_URL
write_static_session = build_static.write_static_session
build_static_session = build_static.build_static_session


def test_kenet_url_default_points_to_starlang_raw_xml():
    assert KENET_URL == "https://raw.githubusercontent.com/StarlangSoftware/TurkishWordNet/master/kenet.xml"


def test_write_static_session_writes_session_file(tmp_path):
    session = {
        "id": "abc123",
        "name": "demo",
        "wordnet": KENET_URL,
        "lexicon": "kenet:1.0",
        "reference_wordnet": None,
        "reference_lexicon": None,
        "extend": False,
        "source_ili": "i35563",
        "target_ili": "i35562",
        "items": [{"lemma": "insan"}],
    }

    result = write_static_session(session, tmp_path)

    assert result["session_path"] == tmp_path / "demo-abc123.json"
    assert result["session_path"].exists()
    assert json.loads(result["session_path"].read_text(encoding="utf-8")) == session
    assert not (tmp_path / "sessions.json").exists()


def test_write_static_session_sanitizes_name_in_filename(tmp_path):
    session = {
        "id": "abc123",
        "name": "WNJA animal/human",
        "items": [],
    }

    result = write_static_session(session, tmp_path)

    assert result["session_path"] == tmp_path / "WNJA_animal_human-abc123.json"


def test_build_static_session_passes_none_lexicon_for_custom_wordnet(monkeypatch, tmp_path):
    captured = {}

    def fake_build_candidate_session(wordnet, source_ili, target_ili, lexicon, name, *rest):
        captured["wordnet"] = wordnet
        captured["lexicon"] = lexicon
        return {
            "id": "custom",
            "name": name,
            "wordnet": wordnet,
            "lexicon": lexicon,
            "reference_wordnet": None,
            "reference_lexicon": None,
            "extend": False,
            "source_ili": source_ili,
            "target_ili": target_ili,
            "items": [],
        }

    monkeypatch.setattr(build_static, "build_candidate_session", fake_build_candidate_session)
    args = argparse.Namespace(
        out=str(tmp_path),
        name="wnja",
        wordnet="/tmp/wnja.xml",
        lexicon=None,
        source_ili="i35563",
        target_ili="i35562",
        reference_wordnet="",
        reference_lexicon=None,
        extend=False,
        display_wordnet="",
        display_lexicon=None,
    )

    build_static_session(args)

    assert captured == {"wordnet": "/tmp/wnja.xml", "lexicon": None}
