"""Tests for the Control UI (milestone 11).

The UI is a static local web dashboard. These tests verify that the required
HTML elements and JavaScript hooks exist and that the script contains the
theme‑toggle logic. No browser is launched; we inspect the source files
directly."""
import re

def test_index_html_contains_required_sections():
    from pathlib import Path
    html_path = Path("app/index.html")
    content = html_path.read_text(encoding="utf-8")

    # Required top‑level sections (IDs) must exist.
    required_ids = [
        "status", "weekly-grades", "strategies",
        "relationships", "auditor", "controls"
    ]
    for rid in required_ids:
        pattern = rf'id="{rid}"'
        assert re.search(pattern, content), f"Missing element with id '{rid}'"

    # Must have a theme toggle button with id="theme-toggle".
    assert re.search(r'id="theme-toggle"', content), "Missing theme toggle button"

    # Ensure the page links to the stylesheet and script.
    assert re.search(r'<link rel="stylesheet" href="style\.css"', content)
    assert re.search(r'<script src="script\.js"></script>', content)


def test_script_contains_theme_toggle_logic():
    from pathlib import Path
    js_path = Path("app/script.js")
    content = js_path.read_text(encoding="utf-8")

    # Look for the click handler that toggles data-theme attribute.
    assert re.search(
        r"themeToggle\.addEventListener\('click',\s*\(\)\s*=>\s*{[^}]*root\.setAttribute\('data-theme',", 
        content,
        re.DOTALL
    ), "Theme toggle handler not found"

    # Verify that the script loads demo_snapshot.json (even if file is empty).
    assert re.search(r"fetch\('data/demo_snapshot\.json'\)", content), "Demo data fetch missing"


def test_style_css_exists_and_defines_theme_variables():
    from pathlib import Path
    css_path = Path("app/style.css")
    content = css_path.read_text(encoding="utf-8")
    # Must define CSS custom properties for light/dark themes.
    assert "--bg-color" in content, "Missing CSS variable for background color"
    assert "--text-color" in content, "Missing CSS variable for text color"
