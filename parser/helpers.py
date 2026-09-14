"""
Common helper functions

"""

from typing import Callable, Iterator
from xml.etree import ElementTree as ET


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


def iterate_entries(xml_path: str, parse_entry_fn: Callable) -> Iterator[Entry]:
    """
    Stream through the XML file, yielding results parsed using the parse_entry_fn.

    Uses iterparse for memory efficiency — does NOT load the whole
    file into memory. Clears processed elements as it goes.
    """
    if parse_entry_fn is None or not callable(parse_entry_fn):
        raise ValueError("parse_entry_fn must be provided.")

    #  TODO: Optimize memory usage by clearing elements after processing
    for event, elem in ET.iterparse(xml_path, events=("end",)):
        entry = parse_entry_fn(elem)
        if entry:
            yield entry
