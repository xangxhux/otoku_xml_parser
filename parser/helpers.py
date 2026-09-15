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
