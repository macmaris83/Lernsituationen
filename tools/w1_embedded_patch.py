"""Keep only W1 in LG05's embedded PDF payloads without altering PDF bytes.

Use transform(repository_relative_path, UTF8_text). No filesystem mutations.
The primary migration owns lesson-data, static HTML, manifest and PDF deletion.
"""
from __future__ import annotations
import json
import re
from pathlib import PurePosixPath

_OTHER_PDF = re.compile(r"(?:[-_]W(?:eg)?[2-5])(?=\.pdf$)", re.I)


def other_path_pdf(path: str) -> bool:
    return bool(_OTHER_PDF.search(path))


def _json_assignment(text: str, name: str, change, *, required=True) -> str:
    match = re.search(r"\bwindow\." + re.escape(name) + r"\s*=\s*", text)
    if not match:
        if required:
            raise ValueError(f"Missing embedded PDF assignment {name}")
        return text
    try:
        value, count = json.JSONDecoder().raw_decode(text[match.end():])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Non-JSON payload for {name}") from exc
    result = change(value)
    replacement = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    return text[:match.end()] + replacement + text[match.end() + count:]


def _keep_one(value):
    if not isinstance(value, dict) or "1" not in value:
        raise ValueError("PDF mode map has no W1 payload")
    unknown = set(value) - {"1", "2", "3", "4", "5"}
    if unknown:
        raise ValueError(f"Unexpected PDF mode keys: {unknown}")
    return {"1": value["1"]}


def _keep_page_one(value):
    if not isinstance(value, dict) or "page:1" not in value:
        raise ValueError("Current phase PDF map has no W1 payload")
    unknown = set(value) - {f"page:{i}" for i in range(1, 6)}
    if unknown:
        raise ValueError(f"Unexpected phase PDF keys: {unknown}")
    return {"page:1": value["page:1"]}


def _keep_time_one(value):
    if not isinstance(value, dict):
        raise ValueError("Expected PDF time map")
    kept = {key: entries for key, entries in value.items() if not other_path_pdf(key)}
    for key, entries in kept.items():
        if any(int(entry.get("mode", 1)) != 1 for entry in entries):
            # A retained PDF must never contain a removed path; do not silently
            # discard coordinates for a mixed PDF and call the result correct.
            raise ValueError(f"Retained PDF contains another mode: {key}")
    return kept


def transform(path: str, text: str) -> str:
    """Return the reduced textual asset, preserving every W1 base64 value."""
    p = PurePosixPath(path)
    if "/LG05/" not in "/" + path:
        return text
    if p.name == "workbook-data.js":
        return _json_assignment(text, "BRC_GOODNOTES_PDF_BY_MODE", _keep_one)
    if p.name == "print-data.js":
        # BRC_PRINT_PDF, when present, already aliases mode 1. Leave it intact.
        return _json_assignment(text, "BRC_PRINT_PDF_BY_MODE", _keep_one)
    if p.parent.name == "goodnotes" and re.fullmatch(r"page-[a-z]+\.js", p.name):
        return _json_assignment(text, "BRC_CURRENT_PDF_FILES", _keep_page_one)
    if p.name == "pdf-task-times-map.js":
        return _json_assignment(text, "BRC_PDF_TIME_MAP", _keep_time_one)
    if p.name == "answer-space.json":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Expected answer-space object")
        for key in data:
            if not re.fullmatch(r"\d+:[1-5]:\d+", key):
                raise ValueError(f"Unexpected answer-space key {key}")
        kept = {key: value for key, value in data.items() if key.split(":")[1] == "1"}
        return json.dumps(kept, ensure_ascii=False, indent=2) + "\n"
    if p.name in {"README.txt", "MOODLE_SETUP.txt", "README_5_STUFEN.txt"}:
        return (text.replace("SCORM 1.2 · fünf Lernwege", "SCORM 1.2 · tradierter Lernweg 1")
                .replace("Gesamt-PDFs sind für alle fünf Lernwege enthalten; der Download wählt den konfigurierten Lernweg.",
                         "Gesamt-PDF und GoodNotes-Arbeitsheft enthalten ausschließlich den tradierten Lernweg 1.")
                .replace("die vollständige aktuelle Phase des zugewiesenen Lernwegs", "die vollständige aktuelle Phase des tradierten Lernwegs 1"))
    return text
