"""
Common helper functions

"""

from typing import Callable, Iterator
import regex as re
import lxml.etree as ET

_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Collapse whitespace runs into a single space."""
    if not text:
        return text
    return _WHITESPACE_RE.sub(" ", text).strip()


def get_text(element, tag: str, default: str = "") -> str:
    """Safely get the text content of a child element."""
    child = element.find(tag)
    if child is not None and child.text:
        return clean_text(child.text)
    return default


def get_entity_text(element, tag: str, default: str = "") -> str:
    """Get the entity reference name from a child element.

    Use this when the parsing was done with resolve_entities=False.
    E.g., <pos>&n;</pos> yields 'n'.
    """
    child = element.find(tag)
    if child is not None and len(child) > 0 and child[0].text:
        raw = clean_text(child[0].text)
        if raw.startswith("&") and raw.endswith(";"):
            raw = raw[1:-1]
        return raw
    return default


def get_texts(element, tag: str) -> list[str]:
    """Get all text contents of matching child elements."""
    results = []
    for child in element.findall(tag):
        if child.text:
            results.append(clean_text(child.text))
    return results


def get_entity_texts(element, tag: str) -> list[str]:
    """Get all entity reference names from matching child elements.

    Use this when the parsing was done with resolve_entities=False.
    E.g., <pos>&n;</pos> yields 'n'.
    """
    results = []
    for child in element.findall(tag):
        if len(child) > 0 and child[0].text:
            raw = clean_text(child[0].text)
            if raw.startswith("&") and raw.endswith(";"):
                raw = raw[1:-1]
            results.append(raw)
    return results


def iterate_entries(xml_path: str) -> Iterator[Entry]:
    """
    Stream through the XML file, yielding results parsed using the parse_entry_fn.

    For memory efficiency, clears processed entries as it goes.
    """
    for event, elem in ET.iterparse(xml_path, resolve_entities=False):
        if elem.tag == "entry":
            yield elem
            # Clear the entry data and it's sub-element's data to free memory
            elem.clear()


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
