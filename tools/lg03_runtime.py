"""Small LG03 adaptations of the approved LG01/LS06 application shell.

The generator should copy ``Reihen/BRC_LG01/LS06/assets`` first and then call
``patch_runtime_assets(package_root)``.  The SCORM, progress, editor, GoodNotes
and AIS implementations are deliberately reused without modification.

Numerical mode values 1..5 are an application contract.  A generator may label
them A..E in its HTML while keeping those values and the phase-workbook names.
"""

from __future__ import annotations

import argparse
import hashlib
from html import escape
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
APP_SOURCE = REPO / "Reihen/BRC_LG01/LS06"

# These are LG01 presentation restrictions, not runtime access-control logic.
# Keep the hidden path badges and overview; restore only the two controls that
# the user explicitly wants the teacher to configure for the new LG03 series.
_HIDDEN_STUDENT_CONTROLS = (
    "body:not([data-teacher]) :is(.mode-badge,.phase-mode-title,.series-ways),"
    "body:not([data-teacher]) label:has([data-student-mode]){display:none!important}"
)
_HIDDEN_PATH_OVERVIEW = (
    "body:not([data-teacher]) :is(.mode-badge,.phase-mode-title,.series-ways)"
    "{display:none!important}"
)
_HIDDEN_TEACHER_CONTROL = (
    "body[data-teacher] label:has([data-allow-mode]){display:none!important}"
)


def patch_runtime_assets(package_root: Path) -> dict[str, object]:
    """Enable the existing configurable path controls in a generated package.

    ``SOZ_CONFIG.allowStudentMode`` still determines student access.  The
    existing teacher checkbox changes that setting and the existing exporter
    persists it in both configuration files.  This operation is idempotent and
    intentionally does not enable student choice by default.
    """
    package_root = Path(package_root)
    css_path = package_root / "assets/styles.css"
    css = css_path.read_text(encoding="utf-8")
    before = css
    if _HIDDEN_STUDENT_CONTROLS in css:
        css = css.replace(_HIDDEN_STUDENT_CONTROLS, _HIDDEN_PATH_OVERVIEW)
    elif _HIDDEN_PATH_OVERVIEW not in css:
        raise ValueError("Expected the approved LG01/LS06 path visibility rules")
    css = css.replace(_HIDDEN_TEACHER_CONTROL, "")
    if css != before:
        css_path.write_text(css, encoding="utf-8")

    # Hashes make it straightforward to verify that pedagogical content and
    # package-specific metadata did not require rewriting the shared engines.
    unchanged = {}
    for name in (
        "runtime.js", "progress.js", "progress-core.js", "teacher.js",
        "export.js", "scorm.js", "scorm-codec.js", "situation.js", "lg01.js",
    ):
        path = package_root / "assets" / name
        if not path.is_file():
            raise FileNotFoundError(path)
        unchanged[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"stylesChanged": css != before, "sharedJavascriptSha256": unchanged}


def patch_shell(source: str, number: int, title: str,
                cache_version: str = "lg03-20261015") -> str:
    """Retarget an LS06 HTML shell without altering its navigation or scripts.

    The teacher shell also contains an old LS03 eyebrow inherited from the
    original business-plan template.  Replace that explicitly so it cannot
    appear in the new series.  New lesson content should be supplied separately
    by the generator; this function does not rewrite the old lesson body.
    """
    if not 1 <= number <= 12:
        raise ValueError("LG03 lesson number must be between 1 and 12")
    lesson = f"LS{number:02d}"
    source = re.sub(
        r"<title>.*?</title>",
        lambda _match: f"<title>{escape(title)} · BBS 1 Aurich</title>",
        source,
        count=1,
        flags=re.DOTALL,
    )
    source = re.sub(r'data-ls-id="[^"]*"',
                    f'data-ls-id="BRC-LG03-{lesson}"', source)
    source = re.sub(r"pdf/LG01_LS\d+_Gesamtdruck_A4\.pdf",
                    f"pdf/LG03_{lesson}_Gesamtdruck_A4.pdf", source)
    source = source.replace(
        "BRC · LG01 · LS03 · Einen Business-Plan erstellen",
        f"BRC · LG03 · {lesson} · {escape(title)}",
    )
    source = re.sub(
        r'((?:assets/(?:runtime|styles|teacher|progress-core|progress|situation))'
        r'\.(?:js|css))\?[^"\s]*',
        lambda match: match[1] + "?v=" + cache_version,
        source,
    )
    return source


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_root", type=Path)
    args = parser.parse_args()
    report = patch_runtime_assets(args.package_root)
    print("LG03 runtime: existing path controls enabled; shared JavaScript preserved.")
    print("Styles changed:", report["stylesChanged"])


if __name__ == "__main__":
    main()
