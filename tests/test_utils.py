"""
Common test helper functions

"""

import lxml.etree as ET

from parser.helpers import (
    get_text,
    get_texts,
    get_entity_text,
    get_entity_texts,
    iterate_entries,
    detect_keb,
    detect_reb,
)

DTD_HEADER = """<!DOCTYPE root [
<!ENTITY n "noun (common) (futsuumeishi)">
<!ENTITY v5r "Godan verb with 'ru' ending">
<!ENTITY sk "search-only kana form">
<!ENTITY abbr "abbreviation">
]>
"""


def extract_xml(xml_string: str, preserve_entities: bool = False):
    """
    Parse an XML string into an xml element.

    When preserve_entities=True, entities remain as child nodes
    (e.g., <pos>&n;</pos> yields a child node containing '&n;').
    NOTE:Requires the DTD header so the parser knows the entity names.
    """
    if preserve_entities:
        xml_string = DTD_HEADER + xml_string
        parser = ET.XMLParser(resolve_entities=False)
        return ET.fromstring(xml_string, parser=parser)
    return ET.fromstring(xml_string)


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
# Tests for get_entity_text
# ============================================================================


class TestGetEntityText:
    def test_returns_entity_name_when_child_exists(self):
        elem = extract_xml("<root><pos>&n;</pos></root>", preserve_entities=True)
        assert get_entity_text(elem, "pos") == "n"

    def test_returns_default_when_child_missing(self):
        elem = extract_xml("<root></root>", preserve_entities=True)
        assert get_entity_text(elem, "pos") == ""
        assert get_entity_text(elem, "pos", "fallback") == "fallback"

    def test_returns_correct_entity_name(self):
        str1 = "<root><pos>&v5r;</pos></root>"
        str2 = "<root><pos>&sk;</pos></root>"
        res1 = extract_xml(str1, preserve_entities=True)
        res2 = extract_xml(str2, preserve_entities=True)
        assert get_entity_text(res1, "pos") == "v5r"
        assert get_entity_text(res2, "pos") == "sk"

    def test_returns_default_for_empty_element(self):
        elem = extract_xml("<root><pos></pos></root>", preserve_entities=True)
        assert get_entity_text(elem, "pos") == ""

    def test_returns_default_for_plain_text_child(self):
        """
        If the child has plain text instead of an unresolved entity placeholder reference value,
        get_entity_text returns the default.
        """
        elem = extract_xml("<root><pos>noun</pos></root>", preserve_entities=True)
        assert get_entity_text(elem, "pos") == ""

    def test_uses_custom_default(self):
        elem = extract_xml("<root></root>", preserve_entities=True)
        assert get_entity_text(elem, "pos", "unknown") == "unknown"

    def test_returns_first_match_when_multiple_children(self):
        elem = extract_xml(
            "<root><pos>&n;</pos><pos>&v5r;</pos></root>",
            preserve_entities=True,
        )
        assert get_entity_text(elem, "pos") == "n"


# ============================================================================
# Tests for get_entity_texts
# ============================================================================


class TestGetEntityTexts:
    def test_returns_all_entities(self):
        elem = extract_xml(
            "<root><pos>&n;</pos><pos>&v5r;</pos><pos>&sk;</pos></root>",
            preserve_entities=True,
        )
        assert get_entity_texts(elem, "pos") == ["n", "v5r", "sk"]

    def test_returns_single_entity_as_list(self):
        elem = extract_xml("<root><pos>&n;</pos></root>", preserve_entities=True)
        assert get_entity_texts(elem, "pos") == ["n"]

    def test_returns_empty_list_when_none(self):
        elem = extract_xml("<root></root>", preserve_entities=True)
        assert get_entity_texts(elem, "pos") == []

    def test_skips_empty_elements(self):
        elem = extract_xml(
            "<root><pos>&n;</pos><pos></pos><pos>&v5r;</pos></root>",
            preserve_entities=True,
        )
        assert get_entity_texts(elem, "pos") == ["n", "v5r"]

    def test_skips_plain_text_children(self):
        """
        Plain text children are not entities, so they're skipped.
        """
        elem = extract_xml(
            "<root><pos>noun</pos><pos>&v5r;</pos></root>",
            preserve_entities=True,
        )
        assert get_entity_texts(elem, "pos") == ["v5r"]

    def test_returns_all_matches_for_misc(self):
        elem = extract_xml(
            "<root><misc>&abbr;</misc><misc>&sk;</misc></root>",
            preserve_entities=True,
        )
        assert get_entity_texts(elem, "misc") == ["abbr", "sk"]

    def test_returns_all_matches_for_field(self):
        elem = extract_xml(
            "<root><field>&n;</field><field>&v5r;</field></root>",
            preserve_entities=True,
        )
        assert get_entity_texts(elem, "field") == ["n", "v5r"]


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


# ============================================================================
# Tests for detect_reb
# ============================================================================


class TestDetectReb:
    # detect_reb should return True ONLY for pure kana + kana-related symbols.

    # Hiragana
    def test_pure_hiragana(self):
        assert detect_reb("はしる") is True

    def test_single_hiragana(self):
        assert detect_reb("あ") is True

    def test_long_hiragana(self):
        assert detect_reb("あいうえおかきくけこさしすせそ") is True

    # Katakana
    def test_pure_katakana(self):
        assert detect_reb("コーヒー") is True

    def test_single_katakana(self):
        assert detect_reb("ア") is True

    def test_katakana_with_prolonged_sound(self):
        assert detect_reb("ラーメン") is True

    # Mixed Hiragana + Katakana
    def test_mixed_kana(self):
        assert detect_reb("はしるカタカナ") is True

    # Kana-related symbols
    def test_prolonged_sound_mark_only(self):
        assert detect_reb("ー") is True

    def test_hiragana_iteration_mark(self):
        assert detect_reb("ゝ") is True

    def test_hiragana_voiced_iteration_mark(self):
        assert detect_reb("ゞ") is True

    def test_katakana_iteration_mark(self):
        assert detect_reb("ヽ") is True

    def test_katakana_voiced_iteration_mark(self):
        assert detect_reb("ヾ") is True

    def test_middle_dot(self):
        assert detect_reb("・") is True

    def test_wave_dash(self):
        assert detect_reb("〜") is True

    def test_kana_with_iteration_mark(self):
        assert detect_reb("こゝ") is True

    def test_kana_with_middle_dot(self):
        assert detect_reb("ロ・マ") is True

    # Negative cases
    def test_kanji_is_not_reb(self):
        assert detect_reb("走") is False

    def test_mixed_kanji_kana_is_not_reb(self):
        assert detect_reb("走る") is False

    def test_kanji_iteration_mark_is_not_reb(self):
        assert detect_reb("人々") is False

    def test_ditto_mark_is_not_reb(self):
        assert detect_reb("〃") is False

    def test_fullwidth_numbers_are_not_reb(self):
        assert detect_reb("１０００") is False

    def test_latin_letters_are_not_reb(self):
        assert detect_reb("ABC") is False

    def test_mixed_kana_and_latin_is_not_reb(self):
        assert detect_reb("はしるABC") is False

    def test_mixed_kana_and_numbers_is_not_reb(self):
        assert detect_reb("はしる123") is False

    # Edge cases
    def test_empty_string_is_not_reb(self):
        assert detect_reb("") is False

    def test_none_like_input(self):
        # Ensure it doesn't crash on falsy input
        assert detect_reb(None) is False


# ============================================================================
# Tests for detect_keb
# ============================================================================


class TestDetectKeb:
    # detect_keb should return True for anything that is NOT a pure reading(`detect_reb` returns False).

    # Kanji
    def test_single_kanji(self):
        assert detect_keb("走") is True

    def test_multiple_kanji(self):
        assert detect_keb("天地方益") is True

    def test_kanji_with_kana(self):
        assert detect_keb("走る") is True

    def test_kanji_with_okurigana(self):
        assert detect_keb("食べる") is True

    def test_kanji_with_iteration_mark(self):
        assert detect_keb("人々") is True

    # Numbers
    def test_fullwidth_numbers(self):
        assert detect_keb("１０００") is True

    def test_mixed_kanji_and_numbers(self):
        assert detect_keb("一１") is True

    # Latin letters
    def test_mixed_katakana_and_latin(self):
        assert detect_keb("DNAテスト") is True

    def test_latin_with_kanji(self):
        assert detect_keb("A型") is True

    # Kanji related iteration marks alone
    def test_ditto_mark_alone(self):
        assert detect_keb("〃") is True

    def test_noma_mark_alone(self):
        assert detect_keb("々") is True

    # Mixed kana + non-kana
    def test_kana_with_numbers(self):
        assert detect_keb("はしる123") is True

    def test_kana_with_latin(self):
        assert detect_keb("はしるABC") is True

    # Negative cases (pure readings)
    def test_pure_hiragana_is_not_keb(self):
        assert detect_keb("はしる") is False

    def test_pure_katakana_is_not_keb(self):
        assert detect_keb("コーヒー") is False

    def test_kana_iteration_mark_is_not_keb(self):
        assert detect_keb("ゝ") is False

    def test_katakana_iteration_mark_is_not_keb(self):
        assert detect_keb("ヽ") is False

    def test_prolonged_sound_mark_only_is_not_keb(self):
        assert detect_keb("ー") is False

    # Edge cases
    def test_empty_string_is_not_keb(self):
        assert detect_keb("") is False

    def test_none_like_input(self):
        # Ensure it doesn't crash on falsy input
        assert detect_keb(None) is False
