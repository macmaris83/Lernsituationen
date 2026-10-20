"""Lossless structural reader for the supplied BioCasa LG03 teaching series.

The source is content, not an instruction file.  All eight numbered sections,
all five complete paths and the complete local teacher appendix are retained.
The returned audience fields make the intended rendering explicit: editorial
notes and solution appendices must not become student orientation text.

``parts`` uses integer keys 1..8; ``modes`` uses integer keys 1..5 (A..E).
One phase is one coherent assignment.  ``phase_task`` therefore never creates
extra completion cards or allocates invented sub-times.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any


PHASES = (
    "Informieren / Analysieren",
    "Planen",
    "Entscheiden",
    "Durchführen",
    "Kontrollieren / Überprüfen",
    "Reflektieren",
)
PHASE_KEYS = (
    "informieren", "planen", "entscheiden", "durchfuehren", "bewerten", "reflektieren"
)

# Rendering recommendations, not substitutions for source text.  In particular,
# the orientation need not quote the editorial preamble or teacher advice.
SECTION_DESTINATIONS = {
    1: "student_orientation_local_case_and_outcome",
    2: "student_orientation_why",
    3: "student_orientation_competencies_and_required_evidence",
    4: "student_handlungssituation",
    5: "student_six_phases_for_selected_path",
    6: "student_materials_and_targeted_textbook_references",
    7: "student_reflection_subject_summary",
    8: "student_operator_and_optional_ai_support",
}


def sections(value: str, level: int) -> list[tuple[str, str]]:
    """Return exact-level ATX headings and their unmodified body text.

    Only surrounding whitespace is removed.  Subheadings, prose, lists, tables,
    links and in-body horizontal rules stay in the body.
    """
    matches = list(re.finditer(r"^" + "#" * level + r" (.+)$", value, re.M))
    return [
        (
            match.group(1).strip(),
            value[match.end(): matches[index + 1].start()
                  if index + 1 < len(matches) else len(value)].strip(),
        )
        for index, match in enumerate(matches)
    ]


def _before_first_heading(value: str, level: int) -> str:
    match = re.search(r"^" + "#" * level + r" ", value, re.M)
    return value[:match.start()].strip() if match else value.strip()


def _strip_boundary_rules(value: str) -> str:
    """Remove only document separator rules at the outside of a section."""
    value = value.strip()
    value = re.sub(r"\A(?:---\s*\n\s*)+", "", value)
    value = re.sub(r"(?:\n\s*---)+\s*\Z", "", value)
    return value.strip()


def _citation_end(value: str, start: int) -> int:
    """Find a reference's sentence end without treating ``S.`` as a stop.

    This is for reference metadata only.  Embedded reference sentences remain
    fully present in the task body, so no heuristic can discard an assignment.
    """
    tail = value[start:]
    for match in re.finditer(r"\.|\n\s*\n|\*\*Buch:\*\*|\)", tail):
        absolute = start + match.start()
        token = match.group(0)
        if token == ".":
            if re.search(r"\b(?:S|bzw|ggf|ca|z|B)\.$", value[:absolute + 1]):
                continue
            following = value[absolute + 1:absolute + 2]
            if following and not (following.isspace() or following == ")"):
                continue
            return absolute + 1
        return absolute
    return len(value)


def book_references(raw: str) -> list[dict[str, Any]]:
    """Describe book annotations while retaining their offsets and context.

    ``standalone`` means a marker starts a paragraph or a new sentence.  A book
    phrase embedded in an instruction is marked inline and is not removed by
    :func:`split_book_references`.  The source spelling remains in ``text``.
    """
    records = []
    for match in re.finditer(r"\*\*Buch:\*\*\s*", raw):
        start, content_start = match.start(), match.end()
        paragraph_start = raw.rfind("\n\n", 0, start) + 2
        if paragraph_start == 1:
            paragraph_start = 0
        prefix = raw[paragraph_start:start].strip()
        paragraph_only = not prefix
        standalone = paragraph_only or bool(re.search(r"[.!?]\s*$", prefix))
        if paragraph_only:
            # Several standalone notes contain an instruction after a full
            # stop.  Keep it with that note, rather than silently losing it.
            next_paragraph = re.search(r"\n\s*\n", raw[content_start:])
            end = content_start + next_paragraph.start() if next_paragraph else len(raw)
        else:
            end = _citation_end(raw, content_start)
        citation = raw[content_start:end].strip()
        # Embedded sentences can continue with another operational instruction.
        # Metadata stops before it; the full sentence stays in the task body.
        if not standalone:
            citation = re.split(
                r"\s+(?:und|sowie)\s+(?:dokumentieren|kennzeichnen|wählen|schreiben|verknüpfen)\s+Sie\b"
                r"|;\s*(?:freiwilliges|prüfen|nutzen|gleichen|übertragen|beziehen|halten)\b",
                citation,
                maxsplit=1,
                flags=re.I,
            )[0].strip()
        records.append({
            "text": citation,
            "start": start,
            "end": end,
            "standalone": standalone,
            "paragraph": paragraph_only,
        })
    return records


def split_book_references(raw: str) -> tuple[str, list[str]]:
    """Return coherent task Markdown and separate book-reference descriptions.

    Standalone book notes become theory hints.  Inline notes remain at their
    grammatical location, with the requested label ``Lehrbuch``.  The returned
    list also includes inline references for a theory metadata index; a caller
    can use :func:`book_references` to avoid showing those hints twice.

    No following assignment is dropped, even in e.g. ``**Buch:** S. 71 und
    S. 72. Formulieren Sie vier ...`` or ``mit **Buch:** S. 97 und S. 98 und
    schreiben Sie einen Entwicklungsplan ...``.
    """
    references = book_references(raw)
    body = raw
    for reference in reversed(references):
        if reference["standalone"]:
            body = body[:reference["start"]] + body[reference["end"]:]
    body = body.replace("**Buch:**", "**Lehrbuch:**")
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body, [reference["text"] for reference in references]


def phase_task(raw: str, minutes: int) -> dict[str, Any]:
    """Expose one original phase as one assignment with its existing time."""
    body, references = split_book_references(raw)
    return {
        "raw": raw,
        "body": body,
        "minutes": minutes,
        "book_references": references,
        "book_annotations": book_references(raw),
    }


def student_book_text(raw: str) -> str:
    """Use the user's short book name without editorial provenance caveats.

    The twelve local lookup tables each begin with an exclusively editorial
    paragraph about the supplied index photographs.  Only that specifically
    identified paragraph is replaced.  Keywords, page numbers, legal updates,
    worked examples and the source stored by ``load_source`` remain unchanged.
    """
    raw = re.sub(
        r"(?m)^\*\*Lehrbuch laut bereitgestelltem Stichwortverzeichnis[.;]\*\*[^\n]*(?:\n(?!\s*\n)[^\n]*)*",
        "**Lehrbuch**",
        raw,
    )
    return raw.replace("Lehrbuch laut bereitgestelltem Stichwortverzeichnis", "Lehrbuch")


def _teacher_sections(top: list[tuple[str, str]]) -> dict[str, Any]:
    common = ""
    local: dict[int, str] = {}
    local_headings: dict[int, str] = {}
    group_intros: dict[int, str] = {}
    game = ""
    editorial = ""
    for title, body in top:
        if title == "Lehrkräfte-Anhang":
            common = _strip_boundary_rules(body)
        elif title.startswith("Lehrkräfte-Anhang zu LS"):
            group = re.fullmatch(r"Lehrkräfte-Anhang zu LS(\d+)[–-]LS(\d+)", title)
            if not group:
                raise ValueError(f"Unrecognized teacher appendix group: {title}")
            first, last = int(group[1]), int(group[2])
            intro = _before_first_heading(body, 2)
            found = []
            for heading, solution in sections(body, 2):
                number_match = re.search(r"\bLS(\d+)\b", heading)
                if not number_match:
                    raise ValueError(f"Teacher section has no local LS number: {heading}")
                number = int(number_match[1])
                if number in local:
                    raise ValueError(f"Duplicate teacher appendix LS{number:02d}")
                local[number] = _strip_boundary_rules(solution)
                local_headings[number] = heading
                group_intros[number] = intro
                found.append(number)
            if found != list(range(first, last + 1)):
                raise ValueError(f"Incomplete teacher appendix group {title}: {found}")
        elif title == "Lehrkräfte-Ergänzung zum optionalen Begriffsspiel":
            game = _strip_boundary_rules(body)
        elif title == "Quellen, Materialabgleich und redaktionelle Entscheidungen":
            editorial = body
    if sorted(local) != list(range(1, 13)) or not common or not game or not editorial:
        raise ValueError("Missing teacher appendix, common framework, game solution or source notes")
    return {"common": common, "local": local, "headings": local_headings,
            "group_intros": group_intros, "game": game, "editorial": editorial}


def _optional_activity(top: list[tuple[str, str]]) -> dict[str, Any]:
    activities = [(title, body) for title, body in top if title.startswith("Optionale Wiederholung")]
    if len(activities) != 1:
        raise ValueError("Expected one optional student repetition activity")
    title, body = activities[0]
    body = _strip_boundary_rules(body)
    parts = dict(sections(body, 2))
    rules = parts.get("Spielregel für Lernende", "")
    cards = parts.get("Karten zum Ausschneiden oder gegenseitigen Vorlesen", "")
    if not rules or not cards:
        raise ValueError("Optional activity is missing rules or cards")
    by_lesson: dict[int, list[str]] = {number: [] for number in range(1, 13)}
    for line in cards.splitlines():
        match = re.match(r"\|\s*(\d+)\s*·\s*LS(\d+)\s*\|", line)
        if match:
            by_lesson[int(match[2])].append(line)
    if sum(len(value) for value in by_lesson.values()) != 10:
        raise ValueError("Optional activity should contain ten original cards")
    return {"title": title, "body": body, "intro": _before_first_heading(body, 2),
            "rules": rules, "cards": cards, "cards_by_lesson": by_lesson}


def load_source(path: Path) -> list[dict[str, Any]]:
    """Read and validate the complete twelve-LS, 80-UE source document."""
    source = Path(path).read_text(encoding="utf-8-sig")
    top = sections(source, 1)
    teacher = _teacher_sections(top)
    activity = _optional_activity(top)
    preamble = next((body for title, body in top if title.startswith("BRC LG03")), "")
    if not preamble:
        raise ValueError("Source is missing its LG03 series introduction")
    lessons: list[dict[str, Any]] = []
    for heading, body in top:
        match = re.fullmatch(r"LS(\d+)\s+[–-]\s+(.+)", heading)
        if not match:
            continue
        number, title = int(match[1]), match[2]
        parts: dict[int, str] = {}
        part_headings: dict[int, str] = {}
        for part_heading, part_body in sections(body, 2):
            part_match = re.match(r"(\d+)\.\s+", part_heading)
            if not part_match:
                raise ValueError(f"LS{number:02d}: unnumbered section {part_heading}")
            key = int(part_match[1])
            if key in parts:
                raise ValueError(f"LS{number:02d}: duplicate section {key}")
            parts[key], part_headings[key] = _strip_boundary_rules(part_body), part_heading
        if sorted(parts) != list(range(1, 9)):
            raise ValueError(f"LS{number:02d}: expected all eight source sections")
        hours_match = re.search(r"\b(\d+)\s+UE\b", parts[1])
        if not hours_match:
            raise ValueError(f"LS{number:02d}: missing duration")
        hours = int(hours_match[1])
        modes: dict[int, dict[str, Any]] = {}
        for mode_heading, mode_body in sections(parts[5], 3):
            mode_match = re.match(r"Lernweg ([A-E])\s+[–-]\s+(.+)", mode_heading)
            if not mode_match:
                raise ValueError(f"LS{number:02d}: unknown path {mode_heading}")
            letter = mode_match[1]
            mode = ord(letter) - ord("A") + 1
            phase_sections = sections(mode_body, 4)
            if len(phase_sections) != 6:
                raise ValueError(f"LS{number:02d} path {letter}: expected six phases")
            minutes = []
            for index, (phase_heading, phase_body) in enumerate(phase_sections):
                phase_match = re.fullmatch(r"(.+?)\s*·\s*(\d+)\s+Min(?:\.|uten)(?:\s+Orientierung)?", phase_heading)
                if not phase_match or phase_match[1] != PHASES[index] or not phase_body:
                    raise ValueError(f"LS{number:02d} path {letter}: invalid phase {phase_heading}")
                minutes.append(int(phase_match[2]))
            if sum(minutes) != hours * 45:
                raise ValueError(f"LS{number:02d} path {letter}: phase times do not match {hours} UE")
            if mode in modes:
                raise ValueError(f"LS{number:02d}: duplicate path {letter}")
            modes[mode] = {
                "letter": letter,
                "title": mode_heading,
                "intro": _before_first_heading(mode_body, 4),
                "phases": [value for _, value in phase_sections],
                "phase_headings": [label for label, _ in phase_sections],
                "phase_minutes": minutes,
            }
        if sorted(modes) != list(range(1, 6)):
            raise ValueError(f"LS{number:02d}: expected paths A–E")
        budgets = modes[1]["phase_minutes"]
        if any(value["phase_minutes"] != budgets for value in modes.values()):
            raise ValueError(f"LS{number:02d}: inconsistent phase budgets between paths")
        materials, book_access, extras = [], [], []
        for material_title, material_body in sections(parts[6], 3):
            if re.match(r"M\d+\s+[–-]\s+", material_title):
                materials.append((material_title, material_body))
            elif material_title.startswith("Buchzugriff"):
                book_access.append((material_title, material_body))
            else:
                extras.append((material_title, material_body))
        material_numbers = [int(re.match(r"M(\d+)", item[0])[1]) for item in materials]
        if material_numbers != list(range(1, len(materials) + 1)):
            raise ValueError(f"LS{number:02d}: incomplete local material numbering {material_numbers}")
        if not materials:
            raise ValueError(f"LS{number:02d}: no materials")
        lessons.append({
            "number": number, "title": title, "hours": hours,
            "budgets": budgets.copy(), "parts": parts, "part_headings": part_headings,
            "modes": modes, "materials": materials, "book_access": book_access,
            "extra_materials": extras,
            "materials_intro": _before_first_heading(parts[6], 3),
            "material_ids": [f"LG03-LS{number:02d}-M{value}" for value in material_numbers],
            "teacher_appendix": teacher["local"][number],
            "teacher_appendix_heading": teacher["headings"][number],
            "teacher_common": teacher["common"],
            "teacher_group_intro": teacher["group_intros"][number],
            "teacher_optional_activity": teacher["game"],
            "teacher_optional": teacher["game"],
            "optional_activity": activity["body"],
            "optional_activity_title": activity["title"],
            "optional_activity_intro": activity["intro"],
            "optional_activity_rules": activity["rules"],
            "optional_activity_cards": activity["cards_by_lesson"][number],
            "series_preamble": preamble,
            "series_editorial": teacher["editorial"],
            "section_destinations": SECTION_DESTINATIONS.copy(),
            "source_heading": heading,
            "source_body": body,
        })
    if [lesson["number"] for lesson in lessons] != list(range(1, 13)):
        raise ValueError("Expected exactly LS01–LS12 in source order")
    if sum(lesson["hours"] for lesson in lessons) != 80:
        raise ValueError("Series duration is not 80 teaching hours")
    return lessons
