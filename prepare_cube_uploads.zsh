#!/usr/bin/env zsh

python ref_list_gen.py

rm -f cache/card_ref.txt
rm -f cache/cube.csv
rm -f cache/cube_csv.log

tr '\t' '\n' < cache/cubes_raw.txt > cache/cubes_all.txt
python unique.py < cache/cubes_all.txt > cache/old_cubes.txt

rm -f cache/cubes_raw.txt
rm -f cache/cubes_all.txt

cat ./lists/* cache/always_include.txt cache/old_cubes.txt > cache/all_cards.txt
# cat ./lists/* > cache/all_cards.txt

python unique.py < cache/all_cards.txt > cache/card_list.txt
python create_cube_csv.py < cache/card_list.txt > cache/card_reference.csv

rm -f cache/all_cards.txt
rm -f cache/card_list.txt
