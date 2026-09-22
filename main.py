"""
XML parser for JMdict and KanjiDic XML files.

Usage:
    python main.py /path/to/JMdict.xml
"""

import sys
from parser import (
    jmdict_parser,
    kanjidic_parser,
    helpers,
)
from utils.timer import Timer


def main(xml_path: str):

    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/JMdict.xml")
        sys.exit(1)

    kanjidic_parser.parse_character()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/JMdict.xml")
        sys.exit(1)

    xml_path = sys.argv[1]

    main(xml_path)
