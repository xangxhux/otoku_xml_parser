"""
Test cases for the KanjiDic parser.

These tests focus on the pure parsing functions — no database required.
They verify that XML elements are correctly transformed into Python objects.
"""

import pytest
from test_utils import extract_xml
from src.otoku_xml_parser.model.kanjidic_entity import (
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
from src.otoku_xml_parser.parser.kanjidic_parser import (
    parse_radical,
    parse_codepoint,
    parse_variant,
    parse_querycode,
    parse_dictionaryref,
    parse_meaning,
    parse_reading,
    parse_misc,
    parse_character,
)

# ============================================================================
# Tests for parse_radical
# ============================================================================


class TestParseRadicalElement:
    def test_parses_radical(self):
        elem = extract_xml('<rad_value rad_type="classical">7</rad_value>')
        result = parse_radical(elem, order_index=0)
        assert isinstance(result, Radical)
        assert result.value == 7
        assert result.rad_type == "classical"
        assert result.order_index == 0

    def test_handles_missing_rad_type(self):
        elem = extract_xml("<rad_value>7</rad_value>")
        result = parse_radical(elem, order_index=0)
        assert result.value == 7
        assert result.rad_type == None
        assert result.order_index == 0


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
        result = parse_reading(elem, order_index=0)
        assert isinstance(result, Reading)
        assert result.value == "ya4"
        assert result.r_type == "pinyin"
        assert result.order_index == 0

    def test_handles_missing_r_type(self):
        elem = extract_xml("<reading>ya4</reading>")
        result = parse_reading(elem, order_index=0)
        assert isinstance(result, Reading)
        assert result.value == "ya4"
        assert result.r_type == None
        assert result.order_index == 0


# ============================================================================
# Tests for parse_meaning
# ============================================================================


class TestParseMeaningElement:
    def test_parses_meaning(self):
        elem = extract_xml('<meaning m_lang="fr">Asie</meaning>')
        result = parse_meaning(elem, order_index=0)
        assert isinstance(result, Meaning)
        assert result.value == "Asie"
        assert result.m_lang == "fr"
        assert result.order_index == 0

    def test_handles_missing_m_lang(self):
        elem = extract_xml("<meaning>ya4</meaning>")
        result = parse_meaning(elem, order_index=0)
        assert isinstance(result, Meaning)
        assert result.value == "ya4"
        assert result.m_lang == "en"
        assert result.order_index == 0


# ============================================================================
# Tests for parse_variant
# ============================================================================


class TestParseVariantElement:
    def test_parses_variant(self):
        elem = extract_xml('<variant var_type="jis208">1-48-19</variant>')
        result = parse_variant(elem, order_index=0)
        assert isinstance(result, Variant)
        assert result.value == "1-48-19"
        assert result.var_type == "jis208"
        assert result.order_index == 0

    def test_handles_missing_var_type(self):
        elem = extract_xml("<variant>1-48-19</variant>")
        result = parse_variant(elem, order_index=0)
        assert isinstance(result, Variant)
        assert result.value == "1-48-19"
        assert result.var_type == None
        assert result.order_index == 0


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

    def test_handles_missing_ref_src(self):
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
        assert result.qc_type == "skip"
        assert result.skip_misclass == "stroke_diff"

    def test_parses_missing_qc_type(self):
        elem = extract_xml('<q_code skip_misclass="stroke_diff">2-10-12</q_code>')
        result = parse_querycode(elem)
        assert isinstance(result, QueryCode)
        assert result.code == "2-10-12"
        assert result.qc_type == None
        assert result.skip_misclass == "stroke_diff"

    def test_parses_missing_skip_misclass(self):
        elem = extract_xml('<q_code qc_type="skip">2-10-12</q_code>')
        result = parse_querycode(elem)
        assert isinstance(result, QueryCode)
        assert result.code == "2-10-12"
        assert result.qc_type == "skip"
        assert result.skip_misclass == None


# ============================================================================
# Tests for parse_misc
# ============================================================================


class TestParseMiscElement:
    def test_parses_undefined_values(self):
        elem = extract_xml("<misc></misc>")
        result = parse_misc(elem)
        assert result.grade == None
        assert result.freq == None
        assert result.jlpt == None
        assert isinstance(result.rad_names, list)
        assert isinstance(result.stroke_counts, list)
        assert isinstance(result.variants, list)
        assert len(result.rad_names) == 0
        assert len(result.stroke_counts) == 0
        assert len(result.variants) == 0

    def test_parses_grade(self):
        elem = extract_xml("<misc><grade>9</grade></misc>")
        result = parse_misc(elem)
        assert result.grade == 9

    def test_parses_jlpt(self):
        elem = extract_xml("<misc><jlpt>2</jlpt></misc>")
        result = parse_misc(elem)
        assert result.jlpt == 2

    def test_parses_freq(self):
        elem = extract_xml("<misc><freq>2000</freq></misc>")
        result = parse_misc(elem)
        assert result.freq == 2000

    def test_parses_multiple_stroke_count(self):
        elem = extract_xml(
            """
            <misc>
                <stroke_count>13</stroke_count>
                <stroke_count>14</stroke_count>
            </misc>
            """
        )
        result = parse_misc(elem)
        assert len(result.stroke_counts) == 2
        assert result.stroke_counts[0] == 13
        assert result.stroke_counts[1] == 14

    def test_parses_multiple_rad_name(self):
        elem = extract_xml(
            """
            <misc>
                <rad_name>のぎ</rad_name>
                <rad_name>のぎへん</rad_name>
            </misc>
            """
        )
        result = parse_misc(elem)
        assert len(result.rad_names) == 2
        assert result.rad_names[0] == "のぎ"
        assert result.rad_names[1] == "のぎへん"

    def test_parses_multiple_variants(self):
        elem = extract_xml(
            """
            <misc>
                <variant var_type="jis208">1-65-33</variant>
                <variant var_type="deroo">1275</variant>
            </misc>
            """
        )
        result = parse_misc(elem)
        assert len(result.variants) == 2
        assert result.variants[0].value == "1-65-33"
        assert result.variants[0].var_type == "jis208"
        assert result.variants[1].value == "1275"
        assert result.variants[1].var_type == "deroo"


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
                <misc></misc>
            </character>
            """
        )
        result = parse_character(elem)
        assert len(result.radicals) == 2
        assert result.radicals[0].value == 32
        assert result.radicals[1].value == 27

    def test_parses_multiple_codepoints(self):
        elem = extract_xml(
            """
            <character>
                <literal>圧</literal>
                <codepoint>
                    <cp_value cp_type="ucs">5727</cp_value>
                    <cp_value cp_type="jis208">1-16-21</cp_value>
                </codepoint>
            </character>
            """
        )
        result = parse_character(elem)
        assert len(result.codepoints) == 2

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
            </character>
            """
        )
        result = parse_character(elem)
        assert len(result.dic_num) == 6

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
            </character>
            """
        )
        result = parse_character(elem)
        assert len(result.query_codes) == 4

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
                    <rad_value rad_type="nelson_c">138</rad_value>
                </radical>
                <misc>
                    <grade>2</grade>
                    <stroke_count>6</stroke_count>
                    <stroke_count>5</stroke_count>
                    <stroke_count>7</stroke_count>                    
                    <variant var_type="jis208">1-76-30</variant>
                    <variant var_type="jis212">1-43-07</variant>
                    <freq>626</freq>
                    <jlpt>3</jlpt>
                    <rad_name>まきがまえ</rad_name>
                    <rad_name>えながまえ</rad_name>
                    <rad_name>どうがまえ</rad_name>
                    <rad_name>けいがまえ</rad_name>
                </misc>
                <dic_number>
                    <dic_ref dr_type="nelson_c">4539</dic_ref>
                    <dic_ref dr_type="moro" m_vol="1" m_page="0525">272</dic_ref>
                </dic_number>
                <query_code>
                    <q_code qc_type="skip" skip_misclass="posn">4-2-4</q_code>
                    <q_code qc_type="deroo">1470</q_code>
                </query_code>
                <reading_meaning>
                    <rmgroup>
                        <reading r_type="vietnam">Tẩu</reading>
                        <reading r_type="ja_on">ソウ</reading>
                        <reading r_type="ja_kun">はし.る</reading>
                        <meaning>run</meaning>
                        <meaning m_lang="es">correr</meaning>
                        <meaning m_lang="pt">corrida</meaning>
                    </rmgroup>
                    <nanori>や</nanori>
                    <nanori>つぎ</nanori>
                    <nanori>つぐ</nanori>
                </reading_meaning>
            </character>
            """
        )
        result = parse_character(elem)

        assert result.literal == "走"

        assert result.misc.jlpt == 3
        assert result.misc.freq == 626
        assert result.misc.grade == 2

        # Codepoints
        assert len(result.codepoints) == 2
        assert result.codepoints[0].value == "8d70"
        assert result.codepoints[0].cp_type == "ucs"
        assert result.codepoints[1].value == "1-33-86"
        assert result.codepoints[1].cp_type == "jis208"

        # Radicals
        assert len(result.radicals) == 2
        assert result.radicals[0].value == 156
        assert result.radicals[0].rad_type == "classical"
        assert result.radicals[0].order_index == 0
        assert result.radicals[1].value == 138
        assert result.radicals[1].rad_type == "nelson_c"
        assert result.radicals[1].order_index == 1

        # Dictionary Refs
        assert len(result.dic_num) == 2
        assert result.dic_num[0].ref_index == "4539"
        assert result.dic_num[0].ref_src == "nelson_c"
        assert result.dic_num[0].moro_page == None
        assert result.dic_num[0].moro_vol == None
        assert result.dic_num[1].ref_index == "272"
        assert result.dic_num[1].ref_src == "moro"
        assert result.dic_num[1].moro_page == "0525"
        assert result.dic_num[1].moro_vol == "1"

        # Query Codes
        assert len(result.query_codes) == 2
        assert result.query_codes[0].code == "4-2-4"
        assert result.query_codes[0].qc_type == "skip"
        assert result.query_codes[0].skip_misclass == "posn"
        assert result.query_codes[1].code == "1470"
        assert result.query_codes[1].qc_type == "deroo"
        assert result.query_codes[1].skip_misclass == None

        # Misc>Stroke Counts
        assert len(result.misc.stroke_counts) == 3
        assert result.misc.stroke_counts[0] == 6
        assert result.misc.stroke_counts[1] == 5
        assert result.misc.stroke_counts[2] == 7

        # Misc>rad_names
        assert len(result.misc.rad_names) == 4
        assert result.misc.rad_names[0] == "まきがまえ"
        assert result.misc.rad_names[1] == "えながまえ"
        assert result.misc.rad_names[2] == "どうがまえ"
        assert result.misc.rad_names[3] == "けいがまえ"

        # Misc>Variants
        assert len(result.misc.variants) == 2
        assert result.misc.variants[0].value == "1-76-30"
        assert result.misc.variants[0].var_type == "jis208"
        assert result.misc.variants[0].order_index == 0
        assert result.misc.variants[1].value == "1-43-07"
        assert result.misc.variants[1].var_type == "jis212"
        assert result.misc.variants[1].order_index == 1

        # Reading_Meanings>Nanori
        assert len(result.reading_meaning.nanori) == 3
        assert result.reading_meaning.nanori[0] == "や"
        assert result.reading_meaning.nanori[1] == "つぎ"
        assert result.reading_meaning.nanori[2] == "つぐ"

        # Reading_Meanings>RMGroup>Readings
        rmgroup = result.reading_meaning.rmgroup
        assert len(rmgroup.readings) == 3
        assert rmgroup.readings[0].value == "Tẩu"
        assert rmgroup.readings[0].r_type == "vietnam"
        assert rmgroup.readings[0].order_index == 0
        assert rmgroup.readings[1].value == "ソウ"
        assert rmgroup.readings[1].r_type == "ja_on"
        assert rmgroup.readings[1].order_index == 1
        assert rmgroup.readings[2].value == "はし.る"
        assert rmgroup.readings[2].r_type == "ja_kun"
        assert rmgroup.readings[2].order_index == 2

        # Reading_Meanings>RMGroup>Meanings
        assert len(rmgroup.meanings) == 3
        assert rmgroup.meanings[0].value == "run"
        assert rmgroup.meanings[0].m_lang == "en"
        assert rmgroup.meanings[0].order_index == 0
        assert rmgroup.meanings[1].value == "correr"
        assert rmgroup.meanings[1].m_lang == "es"
        assert rmgroup.meanings[1].order_index == 1
        assert rmgroup.meanings[2].value == "corrida"
        assert rmgroup.meanings[2].m_lang == "pt"
        assert rmgroup.meanings[2].order_index == 2
