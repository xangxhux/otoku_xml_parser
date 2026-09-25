"""
KANJIDIC XML Parser

Streams through the KANJIDIC XML file, parsing each entry
and inserting it into the database.
"""

import lxml.etree as ElementTree
from ..utils.number import to_int
from ..model.kanjidic_entity import (
    Character,
    Codepoint,
    Radical,
    Variant,
    DictionaryReference,
    QueryCode,
    MiscData,
    ReadingMeaning,
    RMGroup,
    Reading,
    Meaning,
)
from ..parser.helpers import (
    get_text,
    get_texts,
    get_entity_texts,
    clean_text,
)


def parse_codepoint(elem):
    """Parse a <cp_value> element."""
    return Codepoint(
        value=elem.text,
        cp_type=elem.get("cp_type"),
    )


def parse_variant(elem, order_index: int):
    """Parse a <variant> element."""
    return Variant(
        value=elem.text,
        var_type=elem.get("var_type"),
        order_index=order_index,
    )


def parse_radical(elem, order_index: int):
    """Parse a <rad_value> element."""
    return Radical(
        value=int(elem.text),
        rad_type=elem.get("rad_type"),
        order_index=order_index,
    )


def parse_dictionaryref(elem):
    """Parse a <dic_ref> element."""
    return DictionaryReference(
        ref_index=elem.text,
        ref_src=elem.get("dr_type"),
        moro_page=elem.get("m_page"),
        moro_vol=elem.get("m_vol"),
    )


def parse_querycode(elem):
    """Parse a <q_code> element."""
    return QueryCode(
        code=elem.text,
        qc_type=elem.get("qc_type"),
        skip_misclass=elem.get("skip_misclass"),
    )


def parse_reading(elem, order_index: int):
    """Parse a <reading> element."""
    return Reading(
        value=elem.text,
        r_type=elem.get("r_type"),
        order_index=order_index,
    )


def parse_meaning(elem, order_index: int):
    """Parse a <meaning> element."""
    return Meaning(
        value=elem.text,
        m_lang=elem.get("m_lang") or "en",
        order_index=order_index,
    )


def parse_reading_meaning(elem, order_index: int):
    """Parse a <rmgroup> element."""
    na_list = get_texts("nanori")

    rm_list = []
    for rm in elem.findall("rmgroup"):
        re_list = []
        me_list = []
        for re in elem.findall("readings"):
            reading = parse_reading(re)
        for me in elem.findall("meanings"):
            meaning = parse_meaning(re)
        rm_list.append(
            RMGroup(readings=re_list, meanings=me_list),
        )

    return ReadingMeaning(
        nanori=na_list,
        rmgroup=rm_list,
    )


def parse_misc(elem):
    """Parse a <misc> element."""
    grade = get_text(elem, "grade", default=None)
    freq = get_text(elem, "freq", default=None)
    jlpt = get_text(elem, "jlpt", default=None)
    rad_names_list = get_texts(elem, "rad_name")

    stroke_counts_list = []
    for sc in elem.findall("stroke_count"):
        count = to_int(sc.text)
        stroke_counts_list.append(count)

    variant_list = []
    for idx, v in enumerate(elem.findall("variant")):
        variant = parse_variant(v, order_index=idx)
        variant_list.append(variant)

    return MiscData(
        grade=int(grade) if grade is not None else None,
        stroke_counts=stroke_counts_list,
        variants=variant_list,
        freq=int(freq) if freq is not None else None,
        rad_names=rad_names_list,
        jlpt=int(jlpt) if jlpt is not None else None,
    )


def parse_character(elem) -> Character:
    """Parse a <character> element."""
    literal_text = get_text(elem, "literal")
    if not literal_text:
        return None

    character_elem = Character(literal=literal_text)

    # <codepoint> elements
    for cp in elem.findall("codepoint/cp_value"):
        codepoint = parse_codepoint(cp)
        character_elem.codepoints.append(codepoint)

    # <radical> elements
    for idx, rad_elem in enumerate(elem.findall("radical/rad_value")):
        character_elem.radicals.append(parse_radical(rad_elem, idx))

    # <misc> element
    misc_elem = elem.find("misc")
    if misc_elem:
        character_elem.misc = parse_misc(misc_elem)

    # <dic_number> element
    for dr in elem.findall("dic_number/dic_ref"):
        dic_ref = parse_dictionaryref(dr)
        character_elem.dic_num.append(dic_ref)

    # <query_code> element
    for qc in elem.findall("query_code/q_code"):
        q_code = parse_querycode(qc)
        character_elem.query_codes.append(q_code)

    # <reading_meaning> element
    character_elem.reading_meaning.nanori = get_texts(elem, "reading_meaning/nanori")
    rmgroup = elem.find("reading_meaning/rmgroup")
    if rmgroup:
        for idx, reading in enumerate(rmgroup.findall("reading")):
            character_elem.reading_meaning.rmgroup.readings.append(parse_reading(reading, idx))
        for idx, meaning in enumerate(rmgroup.findall("meaning")):
            character_elem.reading_meaning.rmgroup.meanings.append(parse_meaning(meaning, idx))

    return character_elem
