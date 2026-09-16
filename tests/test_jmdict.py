"""
Test cases for the JMdict parser.

These tests focus on the pure parsing functions — no database required.
They verify that XML elements are correctly transformed into Python objects.
"""

import pytest
from test_utils import extract_xml
from model.jmdict_entity import (
    Entry,
    KanjiElement,
    ReadingElement,
    Gloss,
    LanguageSource,
    SenseLink,
    Sense,
)
from parser.jmdict_parser import (
    parse_kanji_element,
    parse_reading_element,
    parse_gloss,
    parse_lsource,
    parse_link,
    parse_sense,
    parse_entry,
)

# ============================================================================
# Tests for parse_kanji_element
# ============================================================================


class TestParseKanjiElement:
    def test_parses_basic_kanji(self):
        elem = extract_xml("<k_ele><keb>走る</keb></k_ele>")
        result = parse_kanji_element(elem)
        assert isinstance(result, KanjiElement)
        assert result.keb == "走る"
        assert result.ke_inf == []
        assert result.ke_pri == []

    def test_parses_kanji_with_info_and_priority(self):
        elem = extract_xml(
            """
            <k_ele>
                <keb>走る</keb>
                <ke_inf>&n;</ke_inf>
                <ke_inf>&v5r;</ke_inf>
                <ke_pri>news1</ke_pri>
                <ke_pri>nf01</ke_pri>
            </k_ele>
        """,
            preserve_entities=True,
        )
        result = parse_kanji_element(elem)
        assert result.keb == "走る"
        assert result.ke_inf == ["n", "v5r"]
        assert result.ke_pri == ["news1", "nf01"]

    def test_handles_missing_keb(self):
        elem = extract_xml(
            "<k_ele><ke_inf>&n;</ke_inf></k_ele>", preserve_entities=True
        )
        result = parse_kanji_element(elem)
        assert result.keb == ""
        assert result.ke_inf == ["n"]


# ============================================================================
# Tests for parse_reading_element
# ============================================================================


class TestParseReadingElement:
    def test_parses_basic_reading(self):
        elem = extract_xml("<r_ele><reb>はしる</reb></r_ele>")
        result = parse_reading_element(elem)
        assert isinstance(result, ReadingElement)
        assert result.reb == "はしる"
        assert result.re_inf == []
        assert result.re_pri == []
        assert result.re_restr == []
        assert result.re_nokanji is False

    def test_parses_reading_with_restrictions(self):
        elem = extract_xml(
            """
            <r_ele>
                <reb>はしる</reb>
                <re_restr>走る</re_restr>
                <re_restr>奔る</re_restr>
                <re_pri>news1</re_pri>
            </r_ele>
        """
        )
        result = parse_reading_element(elem)
        assert result.reb == "はしる"
        assert result.re_restr == ["走る", "奔る"]
        assert result.re_pri == ["news1"]

    def test_parses_nokanji_reading(self):
        elem = extract_xml("<r_ele><reb>はしる</reb><re_nokanji/></r_ele>")
        result = parse_reading_element(elem)
        assert result.re_nokanji is True

    def test_nokanji_false_when_absent(self):
        elem = extract_xml("<r_ele><reb>はしる</reb></r_ele>")
        result = parse_reading_element(elem)
        assert result.re_nokanji is False


# ============================================================================
# Tests for parse_gloss
# ============================================================================


class TestParseGloss:
    def test_parses_simple_gloss(self):
        elem = extract_xml("<gloss>to run</gloss>")
        result = parse_gloss(elem)
        assert isinstance(result, Gloss)
        assert result.text == "to run"
        assert result.lang == "eng"
        assert result.gender is None
        assert result.gloss_type is None

    def test_parses_gloss_with_gender(self):
        elem = extract_xml('<gloss g_gend="masculine">actor</gloss>')
        result = parse_gloss(elem)
        assert result.text == "actor"
        assert result.gender == "masculine"

    def test_parses_gloss_with_type(self):
        elem = extract_xml('<gloss g_type="fig">to run</gloss>')
        result = parse_gloss(elem)
        assert result.gloss_type == "fig"

    def test_parses_gloss_with_language(self):
        elem = extract_xml('<gloss xml:lang="fra">courir</gloss>')
        result = parse_gloss(elem)
        assert result.text == "courir"
        assert result.lang == "fra"

    def test_parses_gloss_with_all_attributes(self):
        elem = extract_xml(
            '<gloss xml:lang="fra" g_gend="masculine" g_type="fig">acteur</gloss>'
        )
        result = parse_gloss(elem)
        assert result.text == "acteur"
        assert result.lang == "fra"
        assert result.gender == "masculine"
        assert result.gloss_type == "fig"


# ============================================================================
# Tests for parse_lsource
# ============================================================================


class TestParseLsource:
    def test_parses_simple_source(self):
        elem = extract_xml("<lsource>computer</lsource>")
        result = parse_lsource(elem)
        assert isinstance(result, LanguageSource)
        assert result.src_text == "computer"
        assert result.src_lang == "eng"
        assert result.is_wasei is False
        assert result.is_partial is False

    def test_parses_wasei_source(self):
        elem = extract_xml('<lsource ls_wasei="y">salaryman</lsource>')
        result = parse_lsource(elem)
        assert result.src_text == "salaryman"
        assert result.is_wasei is True

    def test_parses_partial_source(self):
        elem = extract_xml('<lsource ls_type="part">soft</lsource>')
        result = parse_lsource(elem)
        assert result.src_text == "soft"
        assert result.is_partial is True

    def test_parses_source_with_language(self):
        elem = extract_xml('<lsource xml:lang="ger">Arbeit</lsource>')
        result = parse_lsource(elem)
        assert result.src_text == "Arbeit"
        assert result.src_lang == "ger"

    def test_handles_empty_source(self):
        elem = extract_xml("<lsource/>")
        result = parse_lsource(elem)
        assert result.src_text is None
        assert result.src_lang == "eng"


# ============================================================================
# Tests for parse_link
# ============================================================================


class TestParseLink:
    def test_parses_kanji_only_link(self):
        elem = extract_xml("<xref>生</xref>")
        result = parse_link(elem, "xref")
        assert isinstance(result, SenseLink)
        assert result.link_type == "xref"
        assert result.raw_target == "生"
        assert result.parsed_keb == "生"
        assert result.parsed_reb is None
        assert result.parsed_sense_index is None

    def test_parses_reading_only_link(self):
        elem = extract_xml("<xref>いきる</xref>")
        result = parse_link(elem, "xref")
        assert result.parsed_reb == "いきる"
        assert result.parsed_keb is None

    def test_parses_kanji_and_sense_index(self):
        elem = extract_xml("<ant>何れ・1</ant>")
        result = parse_link(elem, "ant")
        assert result.link_type == "ant"
        assert result.parsed_keb == "何れ"
        assert result.parsed_reb is None
        assert result.parsed_sense_index == 1

    def test_parses_kanji_and_reading(self):
        elem = extract_xml("<xref>生きる・いきる</xref>")
        result = parse_link(elem, "xref")
        assert result.parsed_keb == "生きる"
        assert result.parsed_reb == "いきる"
        assert result.parsed_sense_index is None

    def test_parses_kanji_reading_and_sense_index(self):
        elem = extract_xml("<xref>駆ける・かける・1</xref>")
        result = parse_link(elem, "xref")
        assert result.parsed_keb == "駆ける"
        assert result.parsed_reb == "かける"
        assert result.parsed_sense_index == 1

    def test_handles_empty_link(self):
        elem = extract_xml("<xref/>")
        result = parse_link(elem, "xref")
        assert result == None

    def test_handles_malformed_link(self):
        # Links that don't conform to the expected format should return None
        elem1 = extract_xml("<xref>走る・奔る</xref>")
        elem2 = extract_xml("<xref>走る・2・はしる</xref>")
        elem3 = extract_xml("<xref>走る・走る・走る・走る</xref>")

        result1 = parse_link(elem1, "xref")
        result2 = parse_link(elem2, "xref")
        result3 = parse_link(elem3, "xref")
        assert result1 is None
        assert result2 is None
        assert result3 is None

    def test_ant_link_type(self):
        elem = extract_xml("<ant>生</ant>")
        result = parse_link(elem, "ant")
        assert result.link_type == "ant"


# ============================================================================
# Tests for parse_sense
# ============================================================================


class TestParseSense:
    def test_parses_minimal_sense(self):
        elem = extract_xml(
            """
            <sense>
                <gloss>to run</gloss>
            </sense>
        """
        )
        result = parse_sense(elem, 0)
        assert isinstance(result, Sense)
        assert result.sense_index == 0
        assert len(result.glosses) == 1
        assert result.glosses[0].text == "to run"
        assert result.parts_of_speech == []
        assert result.fields == []

    def test_parses_sense_with_pos(self):
        elem = extract_xml(
            """
            <sense>
                <pos>&n;</pos>
                <pos>&v5r;</pos>
                <gloss>to run</gloss>
            </sense>
        """,
            preserve_entities=True,
        )
        result = parse_sense(elem, 0)
        assert result.parts_of_speech == ["n", "v5r"]

    def test_parses_sense_with_fields(self):
        elem = extract_xml(
            """
            <sense>
                <field>&n;</field>
                <field>&v5r;</field>
                <gloss>phoneme</gloss>
            </sense>
        """,
            preserve_entities=True,
        )
        result = parse_sense(elem, 0)
        assert result.fields == ["n", "v5r"]

    def test_parses_sense_with_misc_and_dialect(self):
        elem = extract_xml(
            """
            <sense>
                <misc>&n;</misc>
                <misc>&v5r;</misc>
                <dial>&abbr;</dial>
                <gloss>abbreviation</gloss>
            </sense>
        """,
            preserve_entities=True,
        )
        result = parse_sense(elem, 0)
        assert result.misc_tags == ["n", "v5r"]
        assert result.dialect_tags == ["abbr"]

    def test_parses_multiple_glosses(self):
        elem = extract_xml(
            """
            <sense>
                <gloss>to run</gloss>
                <gloss>to dash</gloss>
                <gloss>to race</gloss>
            </sense>
        """
        )
        result = parse_sense(elem, 0)
        assert len(result.glosses) == 3
        assert [g.text for g in result.glosses] == ["to run", "to dash", "to race"]

    def test_parses_sense_with_lsource(self):
        elem = extract_xml(
            """
            <sense>
                <lsource xml:lang="eng">computer</lsource>
                <gloss>computer</gloss>
            </sense>
        """
        )
        result = parse_sense(elem, 0)
        assert len(result.language_sources) == 1
        assert result.language_sources[0].src_text == "computer"

    def test_parses_sense_with_links(self):
        elem = extract_xml(
            """
            <sense>
                <xref>生</xref>
                <ant>死</ant>
                <gloss>life</gloss>
            </sense>
        """
        )
        result = parse_sense(elem, 0)
        assert len(result.links) == 2
        link_types = [l.link_type for l in result.links]
        assert "xref" in link_types
        assert "ant" in link_types

    def test_sense_index_is_set(self):
        elem = extract_xml("<sense><gloss>x</gloss></sense>")
        result = parse_sense(elem, 5)
        assert result.sense_index == 5


# ============================================================================
# Tests for parse_entry
# ============================================================================


class TestParseEntry:
    def test_parses_minimal_entry(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>1234567</ent_seq>
                <k_ele><keb>走る</keb></k_ele>
                <r_ele><reb>はしる</reb></r_ele>
                <sense><gloss>to run</gloss></sense>
            </entry>
        """
        )
        result = parse_entry(elem)
        assert isinstance(result, Entry)
        assert result.ent_seq == 1234567
        assert len(result.kanji_elements) == 1
        assert len(result.reading_elements) == 1
        assert len(result.senses) == 1

    def test_returns_none_without_ent_seq(self):
        elem = extract_xml(
            """
            <entry>
                <k_ele><keb>走る</keb></k_ele>
            </entry>
        """
        )
        assert parse_entry(elem) is None

    def test_returns_none_with_invalid_ent_seq(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>not-a-number</ent_seq>
            </entry>
        """
        )
        assert parse_entry(elem) is None

    def test_parses_multiple_kanji_elements(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>1234567</ent_seq>
                <k_ele><keb>走る</keb></k_ele>
                <k_ele><keb>奔る</keb></k_ele>
            </entry>
        """
        )
        result = parse_entry(elem)
        assert len(result.kanji_elements) == 2
        assert result.kanji_elements[0].keb == "走る"
        assert result.kanji_elements[1].keb == "奔る"

    def test_parses_multiple_senses_with_indexes(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>1234567</ent_seq>
                <sense><gloss>to run</gloss></sense>
                <sense><gloss>to dash</gloss></sense>
                <sense><gloss>to race</gloss></sense>
            </entry>
        """
        )
        result = parse_entry(elem)
        assert len(result.senses) == 3
        assert result.senses[0].sense_index == 0
        assert result.senses[1].sense_index == 1
        assert result.senses[2].sense_index == 2

    def test_skips_empty_kanji_elements(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>1234567</ent_seq>
                <k_ele><keb></keb></k_ele>
                <k_ele><keb>走る</keb></k_ele>
            </entry>
        """
        )
        result = parse_entry(elem)
        assert len(result.kanji_elements) == 1
        assert result.kanji_elements[0].keb == "走る"

    def test_skips_empty_reading_elements(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>1234567</ent_seq>
                <k_ele><keb>走る</keb></k_ele>
                <r_ele><reb>はしる</reb></r_ele>
                <r_ele><reb></reb></r_ele>
            </entry>
        """
        )
        result = parse_entry(elem)
        assert len(result.reading_elements) == 1
        assert result.reading_elements[0].reb == "はしる"

    def test_parses_complete_entry(self):
        elem = extract_xml(
            """
            <entry>
                <ent_seq>1234567</ent_seq>
                <k_ele>
                    <keb>走る</keb>
                    <ke_pri>news1</ke_pri>
                </k_ele>
                <k_ele>
                    <keb>奔る</keb>
                </k_ele>
                <r_ele>
                    <reb>はしる</reb>
                    <re_pri>news1</re_pri>
                </r_ele>
                <sense>
                    <pos>&n;</pos>
                    <pos>&v5r;</pos>
                    <field>&n;</field>
                    <misc>&n;</misc>
                    <s_inf>as ...（すると／しては）～（から／ので）</s_inf>
                    <gloss>to run</gloss>
                    <gloss>to dash</gloss>
                    <lsource xml:lang="eng">run</lsource>
                    <xref>駆ける・かける・1</xref>
                </sense>
            </entry>
        """,
            preserve_entities=True,
        )
        result = parse_entry(elem)

        assert result.ent_seq == 1234567

        # Kanji
        assert len(result.kanji_elements) == 2
        assert result.kanji_elements[0].keb == "走る"
        assert result.kanji_elements[0].ke_pri == ["news1"]
        assert result.kanji_elements[1].keb == "奔る"

        # Readings
        assert len(result.reading_elements) == 1
        assert result.reading_elements[0].reb == "はしる"
        assert result.reading_elements[0].re_pri == ["news1"]

        # Sense
        assert len(result.senses) == 1
        sense = result.senses[0]
        assert sense.parts_of_speech == ["n", "v5r"]
        assert sense.fields == ["n"]
        assert sense.misc_tags == ["n"]
        assert sense.s_inf == "as ...（すると／しては）～（から／ので）"
        assert len(sense.glosses) == 2
        assert sense.glosses[0].text == "to run"
        assert sense.glosses[1].text == "to dash"
        assert len(sense.language_sources) == 1
        assert sense.language_sources[0].src_text == "run"
        assert len(sense.links) == 1
        assert sense.links[0].parsed_keb == "駆ける"
        assert sense.links[0].parsed_reb == "かける"
        assert sense.links[0].parsed_sense_index == 1
