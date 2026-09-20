"""
KANJIDIC XML Parser

Streams through the KANJIDIC XML file, parsing each entry
and inserting it into the database.
"""

from model.kanjidic_entity import (
    Character,
    Codepoint,
    Radical,
    Variant,
    DictionaryReference,
    QueryCode,
    RMGroup,
    Reading,
    Meaning,
)


def parse_codepoint():
    raise NotImplementedError()


def parse_variant():
    raise NotImplementedError()


def parse_radical():
    raise NotImplementedError()


def parse_dictionaryref():
    raise NotImplementedError()


def parse_querycode():
    raise NotImplementedError()


def parse_rmgroup():
    raise NotImplementedError()


def parse_reading():
    raise NotImplementedError()


def parse_meaning():
    raise NotImplementedError()


def parse_character() -> Character:
    raise NotImplementedError()
