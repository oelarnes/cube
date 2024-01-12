#!/Users/joel/anaconda3/bin/python
# create_cube_csv.py

# populate card_ref.txt with unique list of cards, then
# usage 'python create_cube_csv.py < card_ref.txt > cache/cube.csv'

import scryfall, sys, logging

logging.basicConfig(filename='cube_csv.log',level=logging.WARNING)

attrs = sys.argv if len(sys.argv[1:]) else scryfall.CUBE_ATTRS

# print(scryfall.join_line([scryfall.get_attr_name(attr) for attr in attrs]))
client = scryfall.get_client()

for line in sys.stdin:
    print(scryfall.card_attr_line(client, line, attrs))
