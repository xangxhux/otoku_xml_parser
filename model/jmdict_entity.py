"""
Data classes representing JMdict entities.
These mirror the XML structure and are used to pass data
between the parser and the database layer.
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class KanjiElement:
    """Represents a <k_ele> element."""

    keb: str  # The kanji text
    ke_inf: list[str] = field(default_factory=list)  # Info tags
    ke_pri: list[str] = field(default_factory=list)  # Priority tags


@dataclass
class ReadingElement:
    """Represents an <r_ele> element."""

    reb: str  # The reading text
    re_inf: list[str] = field(default_factory=list)  # Info tags
    re_pri: list[str] = field(default_factory=list)  # Priority tags
    re_restr: list[str] = field(default_factory=list)  # Kanji restrictions
    re_nokanji: bool = False  # True if no kanji applies


@dataclass
class Gloss:
    """Represents a <gloss> element with its attributes."""

    text: str
    # TODO: Move to enum or constants for language codes 
    lang: str = "eng"  # ISO 639-2 code
    gender: Optional[str] = None  # g_gend attribute
    gloss_type: Optional[str] = None  # g_type attribute


@dataclass
class LanguageSource:
    """Represents an <lsource> element."""

    src_text: Optional[str] = None  # The source word
    src_lang: str = "eng"  # ISO 639-2 code
    is_wasei: bool = False  # ls_wasei="y"
    is_partial: bool = False  # ls_type="part"


@dataclass
class SenseLink:
    """
    Represents a cross-reference link between elements (xref, ant, etc.).
    
    The raw text can be in formats like:
    - '生'                    (kanji only)
    - 'いきる'                (reading only)
    - '生きる・いきる'         (kanji + reading)
    - '何れ・1'               (kanji + sense number)
    - '駆ける・かける・1'      (kanji + reading + sense number)
    """

    # TODO: Move to enum or constants for link types
    link_type: str  # 'xref', 'ant'
    raw_target: str  # The raw string from XML
    parsed_keb: Optional[str] = None  # First part (kanji)
    parsed_reb: Optional[str] = None  # Second part (reading)
    parsed_sense_index: Optional[int] = None  # Third part (sense number)


@dataclass
class Sense:
    """Represents a <sense> element."""

    sense_index: int
    parts_of_speech: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)
    misc_tags: list[str] = field(default_factory=list)
    s_inf: Optional[str] = None  # The sense information
    dialect_tags: list[str] = field(default_factory=list)
    glosses: list[Gloss] = field(default_factory=list)
    language_sources: list[LanguageSource] = field(default_factory=list)
    links: list[SenseLink] = field(default_factory=list) # various cross reference relationships (xref, ant, etc.)


@dataclass
class Entry:
    """Represents a complete <entry> element."""

    ent_seq: int
    kanji_elements: list[KanjiElement] = field(default_factory=list)
    reading_elements: list[ReadingElement] = field(default_factory=list)
    senses: list[Sense] = field(default_factory=list)
