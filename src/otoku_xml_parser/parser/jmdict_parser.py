"""
JMdict XML Parser

Streams through the JMdict XML file, parsing each entry
and inserting it into the database.
"""

import regex as re
from ..utils.number import to_int
from ..model.jmdict_entity import (
    Entry,
    KanjiElement,
    ReadingElement,
    Gloss,
    LanguageSource,
    SenseLink,
    Sense,
)
from ..parser.helpers import (
    get_text,
    get_texts,
    get_entity_texts,
    clean_text,
)


def detect_reb(text: str) -> bool:
    """
    Check if text is valid as a JMdict reading form (reb) element.

    The reb element is more restrictive than the keb element.
    It can only contain kana and kana-related characters.

    The reb element can only contain:
      - Hiragana
      - Katakana
      - ー (prolonged sound mark)
      - ヽ ヾ ゝ ゞ (kana iteration marks)
      - ・ (middle dot)
      - 〜 (wave dash)

    From JMDict(2026-09-03,ln.521)
        This element content is restricted to kana and related
        characters such as chouon and kurikaeshi. Kana usage will be
        consistent between the keb and reb elements; e.g. if the keb
        contains katakana, so too will the reb.
    """
    # \u30FC        ー prolonged sound mark
    # \u30FD        ヽ katakana iteration mark
    # \u30FE        ヾ katakana voiced iteration mark
    # \u309D        ゝ hiragana iteration mark
    # \u309E        ゞ hiragana voiced iteration mark
    # \u30FB        ・ middle dot
    # \u301C        〜 wave dash
    # Characters allowed in a JMdict <reb> element
    _REB_PATTERN = re.compile(
        r"^[\p{Hira}\p{Kana}\u30FC\u30FD\u30FE\u309D\u309E\u30FB\u301C]+$"
    )
    if not text:
        return False
    return bool(_REB_PATTERN.fullmatch(clean_text(text)))


def detect_keb(text: str) -> bool:
    """
    Check if text is valid as a JMdict kanji form (keb) element.

    A valid keb must contain at least one non-kana character,
    but may also contain kana, iteration marks (々, 〃), numbers,
    and in rare cases, letters from other alphabets.

    From JMDict(2026-09-03,ln.521)
        This element will contain a word or short phrase in Japanese
        which is written using at least one non-kana character (usually kanji,
        but can be other characters). The valid characters are
        kanji, kana, related characters such as chouon and kurikaeshi, and
        in exceptional cases, letters from other alphabets.
    """
    if not text:
        return False
    # If it's a valid reading, it can't be a keb
    if detect_reb(clean_text(text)):
        return False
    # Otherwise, it's most likely a keb
    return True


def parse_kanji_element(k_ele) -> KanjiElement:
    """Parse a <k_ele> element."""
    return KanjiElement(
        keb=get_text(k_ele, "keb"),
        ke_inf=get_entity_texts(k_ele, "ke_inf"),
        ke_pri=get_texts(k_ele, "ke_pri"),
    )


def parse_reading_element(r_ele) -> ReadingElement:
    """Parse an <r_ele> element."""
    return ReadingElement(
        reb=get_text(r_ele, "reb"),
        re_inf=get_entity_texts(r_ele, "re_inf"),
        re_pri=get_texts(r_ele, "re_pri"),
        re_restr=get_texts(r_ele, "re_restr"),
        re_nokanji=r_ele.find("re_nokanji") is not None,
    )


def parse_gloss(gloss_elem) -> Gloss:
    """Parse a <gloss> element with its attributes."""
    return Gloss(
        text=clean_text(gloss_elem.text) if gloss_elem.text else "",
        lang=gloss_elem.get("{http://www.w3.org/XML/1998/namespace}lang", "eng"),
        gender=gloss_elem.get("g_gend"),
        gloss_type=gloss_elem.get("g_type"),
    )


def parse_lsource(lsource_elem) -> LanguageSource:
    """Parse an <lsource> element."""
    return LanguageSource(
        src_text=clean_text(lsource_elem.text.strip()) if lsource_elem.text else None,
        src_lang=lsource_elem.get("{http://www.w3.org/XML/1998/namespace}lang", "eng"),
        is_wasei=lsource_elem.get("ls_wasei") == "y",
        is_partial=lsource_elem.get("ls_type") == "part",
    )


def parse_link(link_elem, link_type: str) -> SenseLink:
    """
    Parse a cross-reference element (xref, ant, etc.).
    Empty links or links that don't conform to the expected format will return None.

    The raw text can be in formats like:
      - '生'                    (kanji only)
      - 'いきる'                (reading only)
      - '生きる・いきる'         (kanji + reading)
      - '何れ・1'               (kanji + sense number)
      - 'どこ・１'              (reading + sense number)
      - '駆ける・かける・1'      (kanji + reading + sense number)

    From JMdict on `xref`(2026-09-03,ln.145):
        "This element is used to indicate a cross-reference to another
        entry with a similar or related meaning or sense. The content of
        this element is typically a keb or reb element in another entry. In some
        cases a keb will be followed by a reb and/or a sense number to provide
        a precise target for the cross-reference. Where this happens, a JIS
        "centre-dot" (0x2126) is placed between the components of the
        cross-reference. The target keb or reb must not contain a centre-dot."
    """
    raw = link_elem.text.strip() if link_elem.text else ""

    # Split by the Japanese middle dot (・)
    parts = [p.strip() for p in raw.split("・") if p.strip()]
    if len(parts) == 0 or len(parts) > 3:
        return None  # Malformed link

    parsed_keb = None
    parsed_reb = None
    parsed_sense_index = None

    if len(parts) == 1:
        # Either kanji or reading
        if detect_reb(parts[0]):
            parsed_reb = parts[0]
        else:
            parsed_keb = parts[0]
    elif len(parts) == 2:
        if parts[1].isdigit():
            # Either (kanji, sense_index) or (reading, sense_index)
            if detect_reb(parts[0]):
                parsed_reb = parts[0]
            else:
                parsed_keb = parts[0]
            parsed_sense_index = to_int(parts[1])
        else:
            # Should be (kanji, reading)
            parsed_keb = parts[0]
            if detect_reb(parts[1]):
                parsed_reb = parts[1]
            else:
                return None  # Malformed: second part is not a reading
    elif len(parts) >= 3:
        # (kanji, reading, sense_index)
        parsed_keb = parts[0]
        if detect_reb(parts[1]):
            parsed_reb = parts[1]
        else:
            return None  # Malformed: second part is not a reading
        if parts[2].isdigit():
            parsed_sense_index = to_int(parts[2])
        else:
            return None  # Malformed: third part is not a sense index

    return SenseLink(
        link_type=link_type,
        raw_target=raw,
        parsed_keb=parsed_keb,
        parsed_reb=parsed_reb,
        parsed_sense_index=parsed_sense_index,
    )


def parse_sense(sense_elem, sense_index: int) -> Sense:
    """Parse a <sense> element with all its children."""

    sense = Sense(sense_index=sense_index)
    sense.parts_of_speech = get_entity_texts(sense_elem, "pos")
    sense.fields = get_entity_texts(sense_elem, "field")
    sense.misc_tags = get_entity_texts(sense_elem, "misc")
    sense.s_inf = get_text(sense_elem, "s_inf")
    sense.dialect_tags = get_entity_texts(sense_elem, "dial")

    # Glosses
    for gloss_elem in sense_elem.findall("gloss"):
        gloss = parse_gloss(gloss_elem)
        if gloss.text:
            sense.glosses.append(gloss)

    # Language sources (loanwords)
    for lsource_elem in sense_elem.findall("lsource"):
        sense.language_sources.append(parse_lsource(lsource_elem))

    # Cross-references
    for xref_elem in sense_elem.findall("xref"):
        sense.links.append(parse_link(xref_elem, "xref"))

    for ant_elem in sense_elem.findall("ant"):
        sense.links.append(parse_link(ant_elem, "ant"))

    return sense


def parse_entry(entry_elem) -> Optional[Entry]:
    """
    Parse a complete <entry> element.
    Returns None if the entry is malformed.
    """
    ent_seq_text = to_int(get_text(entry_elem, "ent_seq"))
    if ent_seq_text is None:
        return None

    entry = Entry(ent_seq=ent_seq_text)

    # Kanji elements
    for k_ele in entry_elem.findall("k_ele"):
        ke = parse_kanji_element(k_ele)
        if ke.keb:  # Only add if there's actual kanji
            entry.kanji_elements.append(ke)

    # Reading elements
    for r_ele in entry_elem.findall("r_ele"):
        re = parse_reading_element(r_ele)
        if re.reb:  # Only add if there's an actual reading
            entry.reading_elements.append(re)

    # Senses elements
    for idx, sense_elem in enumerate(entry_elem.findall("sense")):
        entry.senses.append(parse_sense(sense_elem, idx))

    return entry
