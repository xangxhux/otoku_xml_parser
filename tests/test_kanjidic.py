"""
Test cases for the KanjiDic parser.

These tests focus on the pure parsing functions — no database required.
They verify that XML elements are correctly transformed into Python objects.
"""

import pytest
from test_utils import extract_xml
from model.kanjidic_entity import (
    Radical,
    Codepoint,
    Variant,
    QueryCode,
    DictionaryReference,
    Reading,
    Meaning,
    RMGroup,
    Character,
)
from parser.kanjidic_parser import (
    parse_radical,
    parse_codepoint,
    parse_variant,
    parse_querycode,
    parse_dictionaryref,
    parse_meaning,
    parse_reading,
    parse_rmgroup,
    parse_character,
)

# ============================================================================
# Tests for parse_radical
# ============================================================================


class TestParseRadicalElement:
    def test_parses_radical(self):
        elem = extract_xml('<rad_value rad_type="classical">7</rad_value>')
        result = parse_radical(elem)
        assert isinstance(result, Radical)
        assert result.value == 7
        assert result.rad_type == "classical"

    def test_handles_missing_rad_type(self):
        elem = extract_xml("<rad_value>7</rad_value>")
        result = parse_radical(elem)
        assert result.value == 7
        assert result.rad_type == None


# ============================================================================
# Tests for parse_codepoint
# ============================================================================


class TestParseCodepointElement:
    def test_parses_codepoint(self):
        elem = extract_xml('<cp_value cp_type="ucs">4e9c</cp_value>')
        result = parse_codepoint(elem)
        assert isinstance(result, Codepoint)
        assert result.value == "4e9c"
        assert result.cp_type == "ucs"

    def test_handles_missing_cp_type(self):
        elem = extract_xml("<cp_value>4e9c</cp_value>")
        result = parse_codepoint(elem)
        assert isinstance(result, Codepoint)
        assert result.value == "4e9c"
        assert result.cp_type == None


# ============================================================================
# Tests for parse_reading
# ============================================================================


class TestParseReadingElement:
    def test_parses_reading(self):
        elem = extract_xml('<reading r_type="pinyin">ya4</reading>')
        result = parse_reading(elem)
        assert isinstance(result, Reading)
        assert result.value == "ya4"
        assert result.r_type == "pinyin"

    def test_handles_missing_r_type(self):
        elem = extract_xml("<reading>ya4</reading>")
        result = parse_reading(elem)
        assert isinstance(result, Reading)
        assert result.value == "ya4"
        assert result.r_type == None


# ============================================================================
# Tests for parse_meaning
# ============================================================================


class TestParseMeaningElement:
    def test_parses_meaning(self):
        elem = extract_xml('<meaning m_lang="fr">Asie</meaning>')
        result = parse_meaning(elem)
        assert isinstance(result, Meaning)
        assert result.value == "Asie"
        assert result.src_lang == "fr"

    def test_handles_missing_src_lang(self):
        elem = extract_xml("<meaning>ya4</meaning>")
        result = parse_meaning(elem)
        assert isinstance(result, Meaning)
        assert result.value == "ya4"
        assert result.src_lang == "en"


# ============================================================================
# Tests for parse_variant
# ============================================================================


class TestParseVariantElement:
    def test_parses_variant(self):
        elem = extract_xml('<variant var_type="jis208">1-48-19</variant>')
        result = parse_variant(elem)
        assert isinstance(result, Variant)
        assert result.value == "1-48-19"
        assert result.var_type == "jis208"

    def test_handles_missing_var_type(self):
        elem = extract_xml("<variant>1-48-19</variant>")
        result = parse_variant(elem)
        assert isinstance(result, Variant)
        assert result.value == "1-48-19"
        assert result.var_type == None


# ============================================================================
# Tests for parse_dictionaryref
# ============================================================================


class TestParseDictionaryRefElement:
    def test_parses_dict_ref(self):
        elem = extract_xml('<dic_ref dr_type="nelson_c">939</dic_ref>')
        result = parse_dictionaryref(elem)
        assert isinstance(result, DictionaryReference)
        assert result.ref_index == "939"
        assert result.ref_src == "nelson_c"

    def test_handles_missing_src_lang(self):
        elem = extract_xml("<dic_ref>939</dic_ref>")
        result = parse_dictionaryref(elem)
        assert isinstance(result, DictionaryReference)
        assert result.ref_index == "939"
        assert result.ref_src == None

    def test_parses_when_ref_src_moro(self):
        elem = extract_xml(
            '<dic_ref dr_type="moro" m_vol="7" m_page="0393">18981P</dic_ref>'
        )
        result = parse_dictionaryref(elem)
        assert isinstance(result, DictionaryReference)
        assert result.ref_index == "18981P"
        assert result.ref_src == "moro"
        assert result.moro_vol == "7"
        assert result.moro_page == "0393"


# ============================================================================
# Tests for parse_querycode
# ============================================================================


class TestParseQueryCodeElement:
    def test_parses_querycode(self):
        elem = extract_xml(
            '<q_code qc_type="skip" skip_misclass="stroke_diff">2-10-12</q_code>'
        )
        result = parse_querycode(elem)
        assert isinstance(result, QueryCode)
        assert result.code == "2-10-12"
        assert result.q_type == "skip"
        assert result.skip_misclass == "stroke_diff"

    def test_parses_missing_qc_type(self):
        elem = extract_xml('<q_code skip_misclass="stroke_diff">2-10-12</q_code>')
        result = parse_querycode(elem)
        assert isinstance(result, QueryCode)
        assert result.code == "2-10-12"
        assert result.q_type == None
        assert result.skip_misclass == "stroke_diff"

    def test_parses_missing_skip_misclass(self):
        elem = extract_xml('<q_code qc_type="skip">2-10-12</q_code>')
        result = parse_querycode(elem)
        assert isinstance(result, QueryCode)
        assert result.code == "2-10-12"
        assert result.q_type == "skip"
        assert result.skip_misclass == None


# ============================================================================
# Tests for parse_rmgroup
# ============================================================================


class TestParseRMGroupElement:
    def test_parses_rmgroup(self):
        elem = extract_xml(
            """
        <rmgroup>
            <reading r_type="ja_on">キョウ</reading>
            <meaning>contest</meaning>
            <meaning>race</meaning>
        </rmgroup>
        """
        )
        result = parse_rmgroup(elem)
        assert isinstance(result, RMGroup)
        assert len(result.readings) == 1
        assert len(result.meanings) == 2
        assert result.readings[0].value == "キョウ"
        assert result.readings[0].r_type == "ja_on"
        assert result.meanings[0].value == "contest"
        assert result.meanings[1].value == "race"

    def test_handles_element_order(self):
        elem = extract_xml(
            """
        <rmgroup>
            <reading r_type="ja_on">ア</reading>
            <reading r_type="ja_kun">つ.ぐ</reading>
            <meaning>Asia</meaning>
            <meaning>rank next</meaning>
            <meaning>come after</meaning>
        </rmgroup>
        """
        )
        result = parse_rmgroup(elem)
        assert isinstance(result, RMGroup)
        assert result.readings[0].value == "ア"
        assert result.readings[1].value == "つ.ぐ"
        assert result.readings[0].order_index == 0
        assert result.readings[1].order_index == 1
        assert result.meanings[0].value == "Asia"
        assert result.meanings[1].value == "rank next"
        assert result.meanings[1].value == "come after"
        assert result.meanings[0].order_index == 1
        assert result.meanings[1].order_index == 2
        assert result.meanings[1].order_index == 3

    def test_handles_skip_empty_element(self):
        elem = extract_xml(
            """
        <rmgroup>
            <reading>ア</reading>
            <reading></reading>
            <reading>つ.ぐ</reading>
            <meaning>Asia</meaning>
            <meaning></meaning>
        </rmgroup>
        """
        )
        result = parse_rmgroup(elem)
        assert isinstance(result, RMGroup)
        assert len(result.readings) == 2
        assert len(result.meanings) == 1


# ============================================================================
# Tests for parse_character
# ============================================================================


class TestParseCharacter:

    def test_returns_none_without_literal(self):
        elem = extract_xml(
            """
            <character>
                <codepoint>
                    <cp_value cp_type="ucs">59f6</cp_value>
                </codepoint>
                <radical>
                    <rad_value rad_type="classical">38</rad_value>
                </radical>
            </character>
            """
        )
        assert parse_character(elem) is None

    def test_parses_multiple_radical_classifications(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <radical>
                    <rad_value rad_type="classical">32</rad_value>
                    <rad_value rad_type="nelson_c">27</rad_value>
                </radical>
            </character
            """
        )
        result = parse_entry(elem)
        assert len(result.radicals) == 2
        assert result.radicals[0].value == "32"
        assert result.radicals[1].value == "27"

    def test_parses_multiple_codepoints(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <codepoint>
                    <cp_value cp_type="ucs">5727</cp_value>
                    <cp_value cp_type="jis208">1-16-21</cp_value>
                </codepoint>
            </character
        """
        )
        result = parse_entry(elem)
        assert len(result.codepoints) == 2

    def test_parses_multiple_stroke_count(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <misc>
                    <stroke_count>13</stroke_count>
                    <stroke_count>14</stroke_count>
                </misc>
            </character
        """
        )
        result = parse_entry(elem)
        assert len(result.stroke_counts) == 2

    def test_parses_multiple_rad_name(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <misc>
                    <rad_name>のぎ</rad_name>
                    <rad_name>のぎへん</rad_name>
                </misc>
            </character
        """
        )
        result = parse_entry(elem)
        assert len(result.rad_names) == 2

    def test_parses_multiple_dic_name(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <dic_number>
                    <dic_ref dr_type="nelson_n">4121</dic_ref>
                    <dic_ref dr_type="halpern_njecd">3503</dic_ref>
                    <dic_ref dr_type="halpern_kkd">4315</dic_ref>
                    <dic_ref dr_type="halpern_kkld_2ed">2938</dic_ref>
                    <dic_ref dr_type="oneill_names">220</dic_ref>
                    <dic_ref dr_type="moro" m_vol="8" m_page="0522">24906</dic_ref>
                </dic_number>
            </character
        """
        )
        result = parse_entry(elem)
        assert len(result.dic_nums) == 6

    def test_parses_multiple_query_code(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <query_code>
                    <q_code qc_type="skip">4-5-3</q_code>
                    <q_code qc_type="sh_desc">5d0.1</q_code>
                    <q_code qc_type="four_corner">2090.4</q_code>
                    <q_code qc_type="skip" skip_misclass="posn">2-1-4</q_code>
                </query_code>
            </character
        """
        )
        result = parse_entry(elem)
        assert len(result.query_code) == 4

    def test_parses_multiple_variants(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <misc>
                    <variant var_type="jis208">1-65-33</variant>
                    <variant var_type="deroo">1275</variant>
                </misc>
            </character
        """
        )
        result = parse_entry(elem)
        assert len(result.variants) == 2

    def test_parses_complete_character_element(self):
        elem = extract_xml(
            """
            <character>
                <literal>走</literal>
                <codepoint>
                    <cp_value cp_type="ucs">8d70</cp_value>
                    <cp_value cp_type="jis208">1-33-86</cp_value>
                </codepoint>
                <radical>
                    <rad_value rad_type="classical">156</rad_value>
                </radical>
                <misc>
                    <grade>2</grade>
                    <stroke_count>7</stroke_count>
                    <variant var_type="jis208">1-76-65</variant>
                    <freq>626</freq>
                    <jlpt>3</jlpt>
                </misc>
                <dic_number>
                    <dic_ref dr_type="nelson_c">4539</dic_ref>
                    <dic_ref dr_type="nelson_n">5845</dic_ref>
                </dic_number>
                <query_code>
                    <q_code qc_type="skip">2-3-4</q_code>
                    <q_code qc_type="deroo">1470</q_code>
                </query_code>
                <reading_meaning>
                    <rmgroup>
                        <reading r_type="pinyin">zou3</reading>
                        <reading r_type="korean_r">ju</reading>
                        <reading r_type="korean_h">주</reading>
                        <reading r_type="vietnam">Tẩu</reading>
                        <reading r_type="ja_on">ソウ</reading>
                        <reading r_type="ja_kun">はし.る</reading>
                        <meaning>run</meaning>
                        <meaning m_lang="fr">courir</meaning>
                        <meaning m_lang="es">correr</meaning>
                        <meaning m_lang="es">escapar</meaning>
                        <meaning m_lang="es">huir</meaning>
                        <meaning m_lang="pt">Correr</meaning>
                        <meaning m_lang="pt">corrida</meaning>
                    </rmgroup>
                    <nanori>はしり</nanori>
                </reading_meaning>
            </character>
        """
        )
        result = parse_character(elem)

        assert result.literal == "走"
        assert result.jlpt == 3
        assert result.freq == 626
        assert result.grade == 2

        # Codepoints
        assert len(result.codepoints) == 2
        assert result.kanji_elements[0].value == "8d70"
        assert result.kanji_elements[1].value == "1-33-86"
        assert result.kanji_elements[0].cp_type == "ucs"
        assert result.kanji_elements[1].cp_type == "jis208"

        # Radicals
        # Variants
        # Query Codes
        # Stroke Counts
        # rad_names
        # Dictionary Refs
        # Nanori
        # Reading Meanings