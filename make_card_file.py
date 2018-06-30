#!/usr/bin/env python3.6
# make_card_file.py

import scryfall, sys

attrs = sys.argv if len(sys.argv[1:]) else scryfall.DEFAULT_ATTRS

print(scryfall.join_line([scryfall.get_attr_name(attr) for attr in attrs]))
for line in sys.stdin:
    print(scryfall.card_attr_line(line, attrs))
