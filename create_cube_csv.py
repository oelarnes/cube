#!/Users/joel/anaconda3/bin/python
# create_cube_csv.py

# populate card_ref.txt with unique list of cards, then
# usage 'python create_cube_csv.py < card_ref.txt > cache/cube.csv'

from mdu.scryfall import cube_attr_line, sys, logging

logging.basicConfig(filename='cube_csv.log',level=logging.WARNING)

# attrs = sys.argv if len(sys.argv[1:]) else scryfall.CUBE_ATTRS

for line in sys.stdin:
    print(cube_attr_line(line))
