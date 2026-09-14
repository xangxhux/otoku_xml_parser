"""
JMdict XML Parser

Streams through the JMdict XML file, parsing each entry
and inserting it into the database.
"""

from parser.helpers import get_text, get_texts

from model.jmdict_entity import (
    Entry,
    KanjiElement,
    ReadingElement,
    Gloss,
    LanguageSource,
    SenseLink,
    Sense,
)


def parse_kanji_element(k_ele) -> KanjiElement:
    """Parse a <k_ele> element."""
    return KanjiElement(
        keb=get_text(k_ele, "keb"),
        ke_inf=get_texts(k_ele, "ke_inf"),
        ke_pri=get_texts(k_ele, "ke_pri"),
    )


def parse_reading_element(r_ele) -> ReadingElement:
    """Parse an <r_ele> element."""
    return ReadingElement(
        reb=get_text(r_ele, "reb"),
        re_inf=get_texts(r_ele, "re_inf"),
        re_pri=get_texts(r_ele, "re_pri"),
        re_restr=get_texts(r_ele, "re_restr"),
        re_nokanji=r_ele.find("re_nokanji") is not None,
    )


def parse_gloss(gloss_elem) -> Gloss:
    """Parse a <gloss> element with its attributes."""
    return Gloss(
        text=gloss_elem.text.strip() if gloss_elem.text else "",
        lang=gloss_elem.get("{http://www.w3.org/XML/1998/namespace}lang", "eng"),
        gender=gloss_elem.get("g_gend"),
        gloss_type=gloss_elem.get("g_type"),
    )


def parse_lsource(lsource_elem) -> LanguageSource:
    """Parse an <lsource> element."""
    return LanguageSource(
        src_text=lsource_elem.text.strip() if lsource_elem.text else None,
        src_lang=lsource_elem.get("{http://www.w3.org/XML/1998/namespace}lang", "eng"),
        is_wasei=lsource_elem.get("ls_wasei") == "y",
        is_partial=lsource_elem.get("ls_type") == "part",
    )


def parse_link(link_elem, link_type: str) -> SenseLink:
    """
    Parse a cross-reference element (xref, ant, etc.).

    The raw text can be in formats like:
      - '生'                    (kanji only)
      - 'いきる'                (reading only)
      - '生きる・いきる'         (kanji + reading)
      - '何れ・1'               (kanji + sense number)
      - '駆ける・かける・1'      (kanji + reading + sense number)
    """
    raw = link_elem.text.strip() if link_elem.text else ""

    # Split by the Japanese middle dot (・)
    parts = [p.strip() for p in raw.split("・") if p.strip()]

    parsed_keb = None
    parsed_reb = None
    parsed_sense_index = None

    if len(parts) == 1:
        # TODO: Implement logic to determine if it's keb or reb
        parsed_keb = parts[0]
    elif len(parts) == 2:
        """
        Either (kanji, reading) or (kanji, sense_index)

        From JMdict documentation(date:2026-09-03, line 145):
        "This element is used to indicate a cross-reference to another
        entry with a similar or related meaning or sense. The content of
        this element is typically a keb or reb element in another entry. In some
        cases a keb will be followed by a reb and/or a sense number to provide
        a precise target for the cross-reference. Where this happens, a JIS
        "centre-dot" (0x2126) is placed between the components of the
        cross-reference. The target keb or reb must not contain a centre-dot."
        """
        if parts[1].isdigit():
            parsed_keb = parts[0]
            parsed_sense_index = int(parts[1])
        else:
            parsed_keb = parts[0]
            parsed_reb = parts[1]
    elif len(parts) >= 3:
        # (kanji, reading, sense_index)
        parsed_keb = parts[0]
        parsed_reb = parts[1]
        if parts[2].isdigit():
            parsed_sense_index = int(parts[2])

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
    sense.parts_of_speech = get_texts(sense_elem, "pos")
    sense.fields = get_texts(sense_elem, "field")
    sense.misc_tags = get_texts(sense_elem, "misc")
    sense.dialect_tags = get_texts(sense_elem, "dial")

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
    ent_seq_text = get_text(entry_elem, "ent_seq")
    if not ent_seq_text:
        return None

    try:
        ent_seq = int(ent_seq_text)
    except ValueError:
        return None

    entry = Entry(ent_seq=ent_seq)

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

    # Senses
    for idx, sense_elem in enumerate(entry_elem.findall("sense")):
        entry.senses.append(parse_sense(sense_elem, idx))

    return entry
