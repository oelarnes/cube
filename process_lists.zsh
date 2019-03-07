#!/usr/bin/env zsh

rm -f card_ref.txt
rm -f cube.csv
rm -f cube_csv.log

cat ./lists/* | python unique.py > card_ref.txt
python create_cube_csv.py < card_ref.txt > cube.csv
