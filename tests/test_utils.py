"""
Common test helper functions

"""

import xml.etree.ElementTree as ET

from parser.helpers import (
    get_text,
    get_texts,
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
