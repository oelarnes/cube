#!/usr/bin/env zsh

rm -f card_ref.txt
rm -f cube.csv
rm -f cube_csv.log

cat ./lists/* new_cards.txt | python unique.py > card_ref.txt
python create_cube_csv.py < card_ref.txt > share/cube.csv
