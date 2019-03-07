#!/Users/joel/anaconda3/bin/python
# create_cube_csv.py

import scryfall, sys, logging

logging.basicConfig(filename='cube_csv.log',level=logging.WARNING)

attrs = sys.argv if len(sys.argv[1:]) else scryfall.CUBE_ATTRS

print(scryfall.join_line([scryfall.get_attr_name(attr) for attr in attrs]))
for line in sys.stdin:
    print(scryfall.card_attr_line(line, attrs))
