"""Add the current master's work-form metadata without rewriting lesson content.

Only a direct-child ``assignment-social`` element is inserted or replaced.  The
source HTML around it, including task bodies and progress identifiers, is kept
byte-for-byte.  Canonical task bodies are compared within the same phase/path;
the source's own instructions cover unmatched and additional assignments.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
import re

from lxml import html as H


PHASES = (
    "informieren", "planen", "entscheiden", "durchfuehren", "bewerten", "reflektieren",
)
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
_SPACE = re.compile(r"\s+")


def _has_class(node, name):
    return name in (node.get("class") or "").split()


def _find(node, name):
    return next((child for child in node.iter() if _has_class(child, name)), None)


def _normal(value):
    return _SPACE.sub(" ", value).strip()


@dataclass
class _Card:
    start: int
    mode: int
    attrs: dict
    end: int = 0
    body_start: int = 0
    socials: list[tuple[int, int]] = field(default_factory=list)


class _CardScanner(HTMLParser):
    """Locate source ranges; parsing/serialising the page would change prose HTML."""

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0] + [m.end() for m in re.finditer("\n", source)]
        self.stack = []
        self.cards = []
        self.feed(source)
        self.close()
        if any(not card.end or not card.body_start for card in self.cards):
            raise ValueError("Unvollständige Aufgabenkarte: Arbeitsauftrag fehlt.")

    def char_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, tag in _VOID)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, True)

    def _start(self, tag, attrs, closed):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        mode = attrs.get("data-mode-panel", parent.get("mode", 0))
        card = parent.get("card")
        role = None
        position = self.char_offset()
        if tag == "article" and "assignment-frame" in (attrs.get("class") or "").split():
            if card:
                raise ValueError("Verschachtelte Aufgabenkarten werden nicht verändert.")
            card = _Card(position, int(mode or 0), attrs)
            self.cards.append(card)
            role = "card"
        elif card and parent.get("role") == "card":
            if "assignment-body" in (attrs.get("class") or "").split():
                card.body_start = position
                role = "body"
            elif "assignment-social" in (attrs.get("class") or "").split():
                role = "social"
        frame = {"tag": tag, "mode": mode, "card": card, "role": role, "start": position}
        if not closed:
            self.stack.append(frame)

    def handle_endtag(self, tag):
        found = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i]["tag"] == tag), None)
        if found is None:
            return
        end = self.source.find(">", self.char_offset()) + 1
        for frame in self.stack[found:]:
            card = frame.get("card")
            if frame.get("role") == "card":
                card.end = end
            elif frame.get("role") == "social":
                card.socials.append((frame["start"], end))
        del self.stack[found:]


def _command(card):
    body = _find(card, "assignment-body")
    if body is None:
        return ""
    body = deepcopy(body)
    for child in list(body.iterdescendants()):
        if child.getparent() is None:
            continue
        if (_has_class(child, "book-line") or _has_class(child, "book-reference")
                or _has_class(child, "assignment-time") or _has_class(child, "split-context")
                or _has_class(child, "task-shared-context") or "data-split-context" in child.attrib):
            child.drop_tree()
    command = _normal(body.text_content())
    # Older exports added this generic introduction as ordinary prose rather
    # than marking it data-split-context. It carries no work-form information.
    return re.sub(r"^(?:Bearbeiten Sie den folgenden Auftrag:|Beantworten Sie schriftlich:)\s*", "", command)


def _phase_form(panel):
    meta = _find(panel, "phase-meta")
    if meta is None:
        return "", ""
    paragraphs = meta.xpath(".//p")
    paragraph = next((p for p in paragraphs if "Arbeitsform:" in p.text_content()), None)
    if paragraph is None and len(paragraphs) > 1:
        paragraph = paragraphs[1]
    if paragraph is None:
        return "", ""
    value = _normal(paragraph.text_content())
    value = re.sub(r"^Arbeitsform:\s*", "", value)
    icon = next(iter(paragraph.xpath(".//svg")), None)
    return value, H.tostring(icon, encoding="unicode", with_tail=False) if icon is not None else ""


_ICON_PATHS = {
    "individual": '<circle cx="12" cy="6" r="3"/><path d="M5 22v-4a7 7 0 0 1 14 0v4"/>',
    "pair": '<circle cx="7" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M1 22v-5a6 6 0 0 1 12 0v5M15 22v-5a6 6 0 0 1 8-5"/>',
    "partner-groups": '<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><path d="M1 17v-3a4 4 0 0 1 8 0v3M15 17v-3a4 4 0 0 1 8 0v3M8 21h8M14 19l2 2-2 2M10 19l-2 2 2 2"/>',
    "expert-group": '<circle cx="8" cy="7" r="3"/><path d="M2 22v-5a6 6 0 0 1 12 0v5M18 3l1.2 2.5 2.8.4-2 2 .5 2.8-2.5-1.3-2.5 1.3.5-2.8-2-2 2.8-.4z"/>',
    "group": '<circle cx="12" cy="5" r="3"/><circle cx="4" cy="9" r="2"/><circle cx="20" cy="9" r="2"/><path d="M6 22v-5a6 6 0 0 1 12 0v5M1 21v-6a3 3 0 0 1 4-3M23 21v-6a3 3 0 0 0-4-3"/>',
    "plenum": '<circle cx="12" cy="5" r="3"/><path d="M6 22v-5a6 6 0 0 1 12 0v5M2 12h2M20 12h2M3 8l2 1M21 8l-2 1"/>',
    "phase-plan": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>',
}


def _social(kind, label, phase_text, icon=""):
    icon = icon or ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">'
                    + _ICON_PATHS[kind] + "</svg>")
    tooltip = label + ((" · Arbeitsform der Phase: " + phase_text) if phase_text else "")
    return ('<span class="assignment-social" data-workform="' + kind + '" title="'
            + escape(tooltip, quote=True) + '">' + icon + "<small>" + escape(label) + "</small></span>")


def _source_form(command, phase, phase_text, phase_icon):
    """Use explicit source cooperation; inferred choices remain recommendations."""
    value = command.casefold()
    if phase == "reflektieren" or re.search(r"persönliche[nr]? (?:lernbilanz|reflexion|lernreflexion)|individuelle[nr]? (?:reflexion|lernbilanz)", value):
        return "individual", "Einzelarbeit", "persönliche Reflexion", "source"
    if re.search(r"\beinzelarbeit\b|\beinzeln\b|\bjede person\b|\bindividuell (?:bearbeiten|erstellen|dokumentieren)\b", value):
        return "individual", "Einzelarbeit", "ausdrücklicher Einzelauftrag", "source"
    if re.search(r"\bpartnerarbeit\b|\bzu zweit\b|\btandem\b|\bpartnercheck\b", value):
        return "pair", "Partnerarbeit", "ausdrücklicher Partnerauftrag", "source"
    if re.search(r"(?:ander(?:e|en|er)|fremd(?:e|en|er)) (?:gruppe|team)|\bpartnergruppen\b|\bprüfgruppen?\b|\bauditgruppe\b|\bfinanzierungsgremium\b", value):
        return "partner-groups", "Partnergruppen", "ausdrücklicher externer Prüfauftrag", "source"
    if re.search(r"\bexpertengruppen?\b|\bexpertisen?\b", value):
        return "expert-group", "Expertengruppe", "ausdrückliche Expertenarbeit", "source"
    if re.search(r"\bstammgruppe\b", value):
        return "group", "Stammgruppe", "ausdrückliche Stammgruppenarbeit", "source"
    if re.search(r"\bvierergruppen?\b", value):
        return "group", "Vierergruppe", "ausdrückliche Vierergruppenarbeit", "source"
    if re.search(r"\bgemeinsam\b|\b(?:ihr|das|im) team\b|\b(?:ihre|die|der|in der) gruppe\b|\bgruppenarbeit\b", value):
        return "group", "Gruppenarbeit", "ausdrücklicher gemeinsamer Auftrag", "source"
    if ("canva" in value
            or re.search(r"reichen sie (?:das|ihr) (?:überarbeitete )?handlungsergebnis|gemeinsame[srn]? (?:produkt|handlungsergebnis)", value)
            or phase == "durchfuehren" and re.search(r"\b(?:erstellen|gestalten|verfassen|erarbeiten) sie\b", value)):
        return "group", "Gruppenarbeit (Empfehlung)", "Abgabe oder Gestaltung des gemeinsamen Produkts", "source"
    # An original phase plan can prescribe several successive forms. Keep its
    # wording as a tooltip instead of choosing one of them as a new requirement.
    phase_value = phase_text.casefold()
    forms = []
    for pattern, kind, label in [
        (r"\beinzelarbeit\b", "individual", "Einzelarbeit"),
        (r"\bpartnerarbeit\b|\btandem\b", "pair", "Partnerarbeit"),
        (r"\bexpertengruppen?\b", "expert-group", "Expertengruppe"),
        (r"\bpartnergruppen?\b|\bprüfgruppen?\b", "partner-groups", "Partnergruppen"),
        (r"\bvierergruppen?\b", "group", "Vierergruppe"),
        (r"\bstammgruppen?\b", "group", "Stammgruppe"),
        (r"\bgruppenarbeit\b", "group", "Gruppenarbeit"),
        (r"\bplenum\b", "plenum", "Plenum"),
    ]:
        if re.search(pattern, phase_value):
            forms.append((kind, label))
    if len(forms) == 1 and not re.search(r"frei|wähl|empfehl|wechsel|anschließend|danach|zunächst|je nach|offen", phase_value):
        kind, label = forms[0]
        return kind, label, "eindeutige ursprüngliche Phasenarbeitsform", "source"
    return "phase-plan", "Nach Phasenplan", "mehrteilige oder offene ursprüngliche Arbeitsform", "fallback"


def _canonical_match(command, candidates):
    # Never let a tiny generic fragment determine a mandatory social form.
    if len(command) < 32 or len(command.split()) < 4:
        return None, None
    for match_type in ("exact", "contained"):
        matches = [social for text, social in candidates
                   if text == command or (match_type == "contained" and command in text)]
        unique = set(matches)
        if len(unique) == 1:
            return matches[0], match_type
        if matches:
            return None, "mehrdeutige Master-Zuordnung"
    return None, None


def apply_task_workforms(data, canonical_data):
    """Mutate only per-card social metadata; return auditable match counts.

    ``data`` and ``canonical_data`` use the existing ``SOZPAED.pages`` structure.
    No task timing is generated, and no progress metadata is recalculated.
    """
    report = {"tasks": 0, "exact": 0, "contained": 0, "source": 0, "fallback": 0, "unmapped": []}
    for phase in PHASES:
        name = phase + ".html"
        page = data.get("pages", {}).get(name)
        if page is None:
            continue
        canonical = canonical_data.get("pages", {}).get(name, "")
        canonical_cards = _CardScanner(canonical).cards
        candidates = {}
        for card in canonical_cards:
            parsed = H.fromstring(canonical[card.start:card.end])
            social = next((child for child in parsed if _has_class(child, "assignment-social")), None)
            if social is not None:
                # Copy the actual master markup, including its original SVG.
                social_raw = canonical[card.socials[0][0]:card.socials[0][1]] if card.socials else H.tostring(social, encoding="unicode", with_tail=False)
                candidates.setdefault(card.mode, []).append((_command(parsed), social_raw))
        document = H.fragment_fromstring(page, create_parent="div")
        phase_forms = {int(panel.get("data-mode-panel")): _phase_form(panel)
                       for panel in document.xpath(".//*[@data-mode-panel]")}
        replacements = []
        for card in _CardScanner(page).cards:
            report["tasks"] += 1
            parsed = H.fromstring(page[card.start:card.end])
            command = _command(parsed)
            social, match_type = _canonical_match(command, candidates.get(card.mode, []))
            if social is None:
                phase_text, phase_icon = phase_forms.get(card.mode, ("", ""))
                kind, label, reason, match_type = _source_form(command, phase, phase_text, phase_icon)
                social = _social(kind, label, phase_text, phase_icon if kind == "phase-plan" else "")
                report["unmapped"].append({"phase": phase, "mode": card.mode,
                    "taskId": card.attrs.get("data-task-id", ""), "sourceTask": card.attrs.get("data-source-task", ""),
                    "kind": kind, "label": label, "reason": reason, "command": command[:180]})
            report[match_type] += 1
            if card.socials:
                first, *rest = card.socials
                replacements.append((*first, social))
                replacements.extend((start, end, "") for start, end in rest)
            else:
                replacements.append((card.body_start, card.body_start, social))
        for start, end, replacement in sorted(replacements, reverse=True):
            page = page[:start] + replacement + page[end:]
        data["pages"][name] = page
    return report
