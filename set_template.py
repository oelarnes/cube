#!/Users/joel/anaconda3/bin/python
# set_template.py
import sys

import scryfall as sf
import card_attrs as ca

set_ = sys.argv[1]
attrs = sys.argv[2:] if len(sys.argv[2:]) else sf.SET_ATTRS

cards = sf.get_set(set_)

print(sf.join_line([sf.get_attr_name(attr) for attr in attrs]))
for card in cards:
    print(sf.join_line([ca.get_attr_fmt(card, attr) for attr in attrs]))
