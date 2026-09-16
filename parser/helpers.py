"""
Common helper functions

"""

from typing import Callable, Iterator
from xml.etree import ElementTree as ET
import regex as re


def get_text(element, tag: str, default: str = "") -> str:
    """Safely get the text content of a child element."""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default


def get_texts(element, tag: str) -> list[str]:
    """Get all text contents of matching child elements."""
    results = []
    for child in element.findall(tag):
        if child.text:
            results.append(child.text.strip())
    return results


def iterate_entries(xml_path: str) -> Iterator[Entry]:
    """
    Stream through the XML file, yielding results parsed using the parse_entry_fn.

    For memory efficiency, clears processed entries as it goes.
    """
    for event, elem in ET.iterparse(xml_path, events=["end"]):
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
    REB_PATTERN = re.compile(
        r"^[\p{Hira}\p{Kana}\u30FC\u30FD\u30FE\u309D\u309E\u30FB\u301C]+$"
    )
    if not text:
        return False
    return bool(REB_PATTERN.fullmatch(text.strip()))


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
    if detect_reb(text.strip()):
        return False
    # Otherwise, it's most likely a keb
    return True
