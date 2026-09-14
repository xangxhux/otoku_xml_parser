"""
Common helper functions

"""


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
