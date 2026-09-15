"""
Common test helper functions

"""

import xml.etree.ElementTree as ET

from parser.helpers import (
    get_text,
    get_texts,
    iterate_entries,
)


def extract_xml(xml_string: str):
    """Parse a raw XML string into an XML element."""
    return ET.fromstring(xml_string.encode("utf-8"))


# ============================================================================
# Tests for get_text / get_texts
# ============================================================================


class TestGetText:
    def test_returns_text_when_child_exists(self):
        elem = extract_xml("<root><name>hello</name></root>")
        assert get_text(elem, "name") == "hello"

    def test_returns_default_when_child_missing(self):
        elem = extract_xml("<root></root>")
        assert get_text(elem, "name") == ""
        assert get_text(elem, "name", "fallback") == "fallback"

    def test_strips_whitespace(self):
        elem = extract_xml("<root><name>  hello  </name></root>")
        assert get_text(elem, "name") == "hello"

    def test_returns_default_for_empty_element(self):
        elem = extract_xml("<root><name></name></root>")
        assert get_text(elem, "name") == ""

    def test_get_texts_returns_all_matches(self):
        elem = extract_xml("<root><tag>a</tag><tag>b</tag><tag>c</tag></root>")
        assert get_texts(elem, "tag") == ["a", "b", "c"]

    def test_get_texts_returns_empty_list_when_none(self):
        elem = extract_xml("<root></root>")
        assert get_texts(elem, "tag") == []

    def test_get_texts_skips_empty_elements(self):
        elem = extract_xml("<root><tag>a</tag><tag></tag><tag>c</tag></root>")
        assert get_texts(elem, "tag") == ["a", "c"]


# ============================================================================
# Tests for iterate_entries
# ============================================================================


class TestIterateEntries:

    def test_entry_contains_expected_children_when_yielded(self):
        filepath = "tests/test_data/sample_jmdict.xml"
        # Each yielded entry should have its subtree intact at the moment it is yielded.
        for entry in iterate_entries(filepath):
            assert entry.find("ent_seq") is not None
            assert entry.find("r_ele/reb") is not None
            assert entry.find("sense") is not None

    def test_entries_are_cleared_after_yield(self):
        filepath = "tests/test_data/sample_jmdict.xml"
        gen = iterate_entries(filepath)

        first = next(gen)
        # First entry still has children right after being yielded
        assert len(first) > 0

        # Advance the generator — this will trigger cleanup on first entry data
        second = next(gen)

        # first entry should now be empty (cleared)
        assert len(first) == 0

    def test_clear_does_not_affect_next_entry(self):
        filepath = "tests/test_data/sample_jmdict.xml"
        gen = iterate_entries(filepath)

        first = next(gen)
        second = next(gen)

        # Second entry should be intact
        assert second.find("ent_seq") is not None
        assert second.find("ent_seq").text == "2"
        assert second.find("r_ele").find("reb").text == "しんどい"


    def test_all_entries_cleared_after_full_iteration(self):
        filepath = "tests/test_data/sample_jmdict.xml"
        entries = list(iterate_entries(filepath))
        for entry in entries:
            assert len(entry) == 0
