#!/usr/bin/env python3.6
# make_card_file.py

import scryfall, sys

headers = ['Card Name','Color Identity', 'Type', 'CMC', 'Subtypes']

print(scryfall.join_line(headers))
for line in sys.stdin:
    print(scryfall.get_info_line(line))
