# create_cube_csv.py

# populate card_ref.txt with unique list of cards, then
# usage 'python create_cube_csv.py < card_ref.txt > cache/cube.csv'

import sys
import logging

from scryfall import Scryfall

logging.basicConfig(filename='cube_csv.log',level=logging.WARNING)

scryfall = Scryfall()
seen_names = set()

for line in sys.stdin:
    split = line.strip('\n').split('|')
    card_name = split[0].strip()
    if not card_name:
        continue

    set_code = split[1] if len(split) >= 2 else None
    card = scryfall.get_card(card_name, set=set_code)

    # multiple input names (e.g. reskins, flavor names) can resolve to the
    # same card; only emit each once
    if card.name in seen_names:
        continue
    seen_names.add(card.name)

    print(card.cube_attr_line)
