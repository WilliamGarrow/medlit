"""Regression tests for issue #1: malformed structured-summary responses."""

from app.services.summary_parser import parse_summary_sections

CLEAN = '[{"heading": "Your Conditions", "body": "All fine."}]'

LITERAL_NEWLINES = (
    '[{"heading": "Your Conditions", "body": "First paragraph.\n\n'
    'Second paragraph with detail."}]'
)

FENCED = "```json\n" + CLEAN + "\n```"

PREFIXED = "Here is your summary:\n" + CLEAN

TRAILING_COMMA = '[{"heading": "Your Conditions", "body": "All fine.",},]'


def test_clean_json_parses():
    sections, text = parse_summary_sections(CLEAN)
    assert sections and sections[0]["icon"] == "conditions"
    assert text == "All fine."


def test_literal_newlines_inside_strings_parse():
    """The issue #1 case: real newlines in string values."""
    sections, text = parse_summary_sections(LITERAL_NEWLINES)
    assert sections is not None
    assert "Second paragraph" in sections[0]["body"]
    assert not text.startswith("[")


def test_fenced_json_parses():
    sections, _ = parse_summary_sections(FENCED)
    assert sections is not None


def test_prefixed_prose_parses():
    sections, _ = parse_summary_sections(PREFIXED)
    assert sections is not None


def test_trailing_commas_parse():
    sections, _ = parse_summary_sections(TRAILING_COMMA)
    assert sections is not None


def test_garbage_falls_back_to_raw():
    sections, text = parse_summary_sections("I could not produce a summary.")
    assert sections is None
    assert text == "I could not produce a summary."
