from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .wordnet_service import EMPTY_LINK_TYPE, LINK_TYPES


class AnnotationStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, session_id: str) -> dict[str, Any] | None:
        return self._read().get(session_id)

    def list_sessions(self) -> list[dict[str, Any]]:
        sessions = []
        for session in self._read().values():
            items = session.get("items", [])
            counts = {"done": 0, "incomplete": 0, "ignore": 0, "open": 0}
            for item in items:
                counts[item.get("status", "open")] = counts.get(item.get("status", "open"), 0) + 1
            sessions.append(
                {
                    "id": session["id"],
                    "name": session.get("name") or session["id"],
                    "wordnet": session.get("wordnet", ""),
                    "lexicon": session.get("lexicon", ""),
                    "reference_wordnet": session.get("reference_wordnet", ""),
                    "reference_lexicon": session.get("reference_lexicon", ""),
                    "extend": session.get("extend", False),
                    "source_ili": session.get("source_ili", ""),
                    "target_ili": session.get("target_ili", ""),
                    "total": len(items),
                    "counts": counts,
                }
            )
        return sorted(sessions, key=lambda session: session["name"].casefold())

    def save_session(self, session: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        existing = data.get(session["id"], {})
        by_lemma = {item["lemma"]: item for item in existing.get("items", [])}
        merged = deepcopy(session)
        for item in merged["items"]:
            old = by_lemma.get(item["lemma"])
            if old:
                item["links"] = old.get("links", {})
                item["comment"] = old.get("comment", "")
                item["sense_annotations"] = old.get("sense_annotations", {})
                item["status"] = old.get("status", "open")
        data[session["id"]] = merged
        self._write(data)
        return merged

    def set_link(self, session_id: str, lemma: str, source: str, target: str, link_type: str) -> dict[str, Any]:
        if link_type != EMPTY_LINK_TYPE and link_type not in LINK_TYPES:
            raise ValueError(f"Unsupported link type: {link_type}")
        data = self._read()
        item = self._find_item(data, session_id, lemma)
        key = f"{source}::{target}"
        if link_type == EMPTY_LINK_TYPE:
            item.setdefault("links", {}).pop(key, None)
        else:
            item.setdefault("links", {})[key] = {
                "source": source,
                "target": target,
                "type": link_type,
            }
        self._write(data)
        return item

    def set_comment(self, session_id: str, lemma: str, comment: str) -> dict[str, Any]:
        data = self._read()
        item = self._find_item(data, session_id, lemma)
        item["comment"] = comment
        self._write(data)
        return item

    def set_sense_annotation(
        self,
        session_id: str,
        lemma: str,
        sense_id: str,
        comment: str,
        bad_sense: bool,
    ) -> dict[str, Any]:
        data = self._read()
        item = self._find_item(data, session_id, lemma)
        annotations = item.setdefault("sense_annotations", {})
        if comment or bad_sense:
            annotations[sense_id] = {
                "comment": comment,
                "bad_sense": bad_sense,
            }
        else:
            annotations.pop(sense_id, None)
        self._write(data)
        return item

    def set_status(self, session_id: str, lemma: str, status: str) -> dict[str, Any]:
        if status not in {"done", "incomplete", "ignore", "open"}:
            raise ValueError(f"Unsupported status: {status}")
        data = self._read()
        item = self._find_item(data, session_id, lemma)
        item["status"] = status
        self._write(data)
        return item

    def _find_item(self, data: dict[str, Any], session_id: str, lemma: str) -> dict[str, Any]:
        session = data.get(session_id)
        if not session:
            raise KeyError(f"Unknown session: {session_id}")
        for item in session.get("items", []):
            if item["lemma"] == lemma:
                return item
        raise KeyError(f"Unknown lemma in session: {lemma}")

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        with self.path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        tmp.replace(self.path)
