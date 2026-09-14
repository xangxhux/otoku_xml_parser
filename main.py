"""
XML parser for JMdict and KanjiDic XML files.

Usage:
    python main.py /path/to/JMdict.xml
"""

import sys
from parser import jmdict_parser, helpers


def main(xml_path: str):

    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/JMdict.xml")
        sys.exit(1)

    count = 0
    for entry in helpers.iterate_entries(
        sys.argv[1], parse_entry_fn=jmdict_parser.parse_entry
    ):
        print(entry)
        print("\n")
        count += 1

    print(f"Total entries parsed: {count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/JMdict.xml")
        sys.exit(1)

    xml_path = sys.argv[1]

    main(xml_path)
