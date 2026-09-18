"""
Data classes representing KANJIDIC entities.
These mirror the XML structure and are used to pass data
between the parser and the database layer.
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Codepoint:
    """Represents a <cp_value> element.

    `cp_type` possible values:
    - jis208: JIS X 0208-1997 - kuten coding (p-nn-nn)
    - jis212: JIS X 0212-1990 - kuten coding (p-nn-nn)
    - jis213: JIS X 0213-2000 - kuten coding (p-nn-nn)
    - ucs:    Unicode 4.0 - hex coding (4 or 5 hexadecimal digits)
    """

    value: str  # Codepoint value in the target standard
    cp_type: str  # Codepoint type


@dataclass
class Radical:
    """Represents a <rad_value> element.

    `rad_type` possible values:
    - classical
    - nelson_c
    """

    value: int  # Radical number, range 1-214
    rad_type: str  # Radical classification system
    order_index: int

@dataclass
class Variant:
    """Represents the <variant> element.

    Covers things like simplified/traditional forms, old forms,
    and other orthographic variants.

    `var_type` possible values:
    - jis208:   in JIS X 0208 - kuten coding
    - jis212:   in JIS X 0212 - kuten coding
    - jis213:   in JIS X 0213 - kuten coding
    - deroo:    De Roo number - numeric
    - njecd:    Halpern NJECD index number - numeric
    - s_h:      The Kanji Dictionary (Spahn & Hadamitzky) - descriptor
    - nelson_c: "Classic" Nelson - numeric
    - oneill:   Japanese Names (O'Neill) - numeric
    - ucs:      Unicode codepoint- hex
    """

    value: str  # The variant character or form
    var_type: str  # Variant type
    order_index: int

@dataclass
class DictionaryReference:
    """Represents the <dic_ref> element.

    A reference to this kanji in an external dictionary.

    Used to cross-reference the kanji against printed and digital
    dictionaries such as Nelson, Halpern, Heisig, Morohashi, etc.

    `ref_src` possible values:
    - nelson_c:         "Modern Reader's Japanese-English Character Dictionary",
                        edited by Andrew Nelson (now published as the "Classic"
                        Nelson).
    - nelson_n:         "The New Nelson Japanese-English Character Dictionary",
                        edited by John Haig.
    - halpern_njecd:    "New Japanese-English Character Dictionary",
                        edited by Jack Halpern.
    - halpern_kkd:      "Kodansha Kanji Dictionary", (2nd Ed. of the NJECD)
                        edited by Jack Halpern.
    - halpern_kkld:     "Kanji Learners Dictionary" (Kodansha) edited by
                        Jack Halpern.
    - halpern_kkld_2ed: "Kanji Learners Dictionary" (Kodansha), 2nd edition
                        (2013) edited by Jack Halpern.
    - heisig:           "Remembering The  Kanji"  by  James Heisig.
    - heisig6:          "Remembering The  Kanji, Sixth Ed."  by  James Heisig.
    - gakken:           "A New Dictionary of Kanji Usage" (Gakken)
    - oneill_names:     "Japanese Names", by P.G. O'Neill.
    - oneill_kk:        "Essential Kanji" by P.G. O'Neill.
    - moro:             "Daikanwajiten" compiled by Morohashi. For some kanji two
                        additional attributes are used: m_vol:  the volume of the
                        dictionary in which the kanji is found, and m_page: the page
                        number in the volume.
    - henshall:         "A Guide To Remembering Japanese Characters"
                        by Kenneth G.  Henshall.
    - sh_kk:            "Kanji and Kana" by Spahn and Hadamitzky.
    - sh_kk2:           "Kanji and Kana" by Spahn and Hadamitzky (2011 edition).
    - sakade:           "A Guide To Reading and Writing Japanese"
                        edited by Florence Sakade.
    - jf_cards:         Japanese Kanji Flashcards, by Max Hodges and Tomoko Okazaki. (Series 1)
    - henshall3:        "A Guide To Reading and Writing Japanese"
                        3rd	edition, edited by Henshall, Seeley and De Groot.
    - tutt_cards:       Tuttle Kanji Cards, compiled by Alexander Kask.
    - crowley:          "The Kanji Way to Japanese Language Power" by Dale Crowley.
    - kanji_in_context: "Kanji in Context" by Nishiguchi and Kono.
    - busy_people:      "Japanese For Busy People" vols I-III, published
                        by the AJLT. The codes are the volume.chapter.
    - kodansha_compact: the "Kodansha Compact Kanji Guide".
    - maniette:         codes from Yves Maniette's "Les Kanjis dans la tete" French adaptation of Heisig.
    """

    ref_index: str  # The page index in the referenced dictionary
    ref_src: str  # Source dictionary code
    moro_vol: str  # Morohashi volume (only used for Morohashi references)
    moro_page: str  # Morohashi page (only used for Morohashi references)


@dataclass
class QueryCode:
    """Represents the <q_code> element.

    `q_type` possible values:
    - skip:        Halpern's SKIP(System of Kanji Indexing by Patterns) code: n-nn-nn
    - sh_desc:     The Kanji Dictionary(Tuttle 1996) by Spahn and Hadamitzky : nxnn.n
    - four_corner: The "Four Corner"(1928) by Wang Chen
    - deroo:       "2001 Kanji" by Joseph De Roo
    - misclass:    possible misclassification of the kanji
    """

    code: str  # The query code value
    q_type: str = None # Query code system
    skip_misclass: str = None  # Optional SKIP misclassification flag (may be None)


@dataclass
class Reading:
    """Represents the <reading> element.

    `r_type` possible values:
    - pinyin:   modern pinyin romanization of onyomi
    - korean_r: kanji reading in romanized korean
    - korean_h: kanji reading in hangul
    - vietnam:  vietnamese readings
    - ja_on:    onyomi in katana
    - ja_kun:   kunyomi in hiragana
    """

    value: str  # The reading itself, e.g. "いきる" or "セイ"
    r_type: str  # Reading type
    order_index: int = None
    # on_type    # (UNUSED)
    # r_status   # (UNUSED)


@dataclass
class Meaning:
    """Represents the <meaning> element.

    KANJIDIC primarily provides English meanings, but the schema
    allows for other languages via the `src_lang` field(ISO 639-1 code).
    """

    value: str
    src_lang: str = "en"  # ISO 639-1 language code (default: English)
    order_index: int = None


@dataclass
class RMGroup:
    """Represents the <rmgroup> element.

    KANJIDIC groups certain readings together with their associated
    meanings.
    """

    readings: list[Reading] = field(default_factory=list)
    meanings: list[Meaning] = field(default_factory=list)


@dataclass
class Character:
    """Represents the <character> element.

    A single kanji character and all its associated metadata.

    This is the top-level entity for KANJIDIC parsing, analogous to
    `Entry` in JMdict. Each Character corresponds to one <character>
    element in the KANJIDIC XML.
    """

    # The kanji character itself
    literal: str

    # Old JLPT level (1-4) at which the kanji was tested. The old
    # JLPT system was replaced in 2010, but KANJIDIC still uses it.
    jlpt: int

    # Frequency rank of the kanji in newspapers
    # (1 = most common, 2500(2501)=least common).
    # May be None if the kanji isn't in the frequency list.
    freq: int

    # Unicode (and legacy) codepoints for this character. A kanji
    # may have multiple entries here for different encodings.
    codepoints: list[Codepoint] = field(default_factory=list)

    # Radical classifications for the kanji.
    radicals: list[Radical] = field(default_factory=list)

    # School grade level at which the kanji is taught (1-6 for
    # elementary, 8 for middle school, 9-10 for jinmeiyō).
    # This field will be missing on some kanjis.
    grade: int = None

    # Number of strokes. Usually a single value, but can be a list
    # where the first is the accepted stroke count
    # and subsequent ones are common miscounts.
    stroke_counts: list[int] = field(default_factory=list)

    # Name(s) of the radical in Japanese.
    rad_names: list[str] = field(default_factory=list)

    # References to this kanji in external dictionaries. Allows
    # cross-referencing against Nelson, Halpern, Heisig, etc.
    dic_nums: list[DictionaryReference] = field(default_factory=list)

    # Query codes (SKIP, Four-Corner, etc.) for shape-based lookup.
    query_codes: list[QueryCode] = field(default_factory=list)

    # Orthographic variants of the kanji.
    variants: list[Variant] = field(default_factory=list)

    # Grouped readings and their associated meanings.
    reading_meanings: list[RMGroup] = field(default_factory=list)

    # Readings used only in Japanese personal names (nanori).
    # Note: This program parses this field as a direct sub-child of <character>
    #       instead of a sub-child of `<reading_meaning>` (as in KANJIDIC)
    nanori: list[str] = field(default_factory=list)
