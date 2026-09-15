"""
XML parser for JMdict and KanjiDic XML files.

Usage:
    python main.py /path/to/JMdict.xml
"""

import sys
from parser import jmdict_parser, helpers
from utils.timer import Timer


def main(xml_path: str):

    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/JMdict.xml")
        sys.exit(1)

    count = 0
    with Timer() as t:
        for entry in helpers.iterate_entries(sys.argv[1]):
            parsed_entry = jmdict_parser.parse_entry(entry)
            # print("entry", entry, "\n")
            count += 1

    print(f"Total entries parsed: {count}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/JMdict.xml")
        sys.exit(1)

    xml_path = sys.argv[1]

    main(xml_path)
