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
