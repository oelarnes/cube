#!/usr/bin/env zsh
if [ "$1" != '' ]; then
    CUBE_ENV=$1
fi

if [ "$CUBE_ENV" = '' ]; then
    CUBE_ENV=joel
fi

CACHE_DIR=$(jq -r .$CUBE_ENV.cache_dir < cube_config.json)

python ref_list_gen.py $CUBE_ENV

rm -f $CACHE_DIR/card_ref.txt
rm -f $CACHE_DIR/cube.csv
rm -f $CACHE_DIR/cube_csv.log

tr '\t' '\n' < $CACHE_DIR/cubes_raw.txt > $CACHE_DIR/cubes_all.txt
python unique.py < $CACHE_DIR/cubes_all.txt > $CACHE_DIR/old_cubes.txt

cat $CACHE_DIR/lists/* $CACHE_DIR/always_include.txt $CACHE_DIR/old_cubes.txt > $CACHE_DIR/all_cards.txt
# cat ./lists/* > $CACHE_DIR/all_cards.txt

python unique.py < $CACHE_DIR/all_cards.txt > $CACHE_DIR/card_list.txt
python create_cube_csv.py < $CACHE_DIR/card_list.txt > $CACHE_DIR/card_reference.csv

rm -f $CACHE_DIR/all_cards.txt
rm -f $CACHE_DIR/card_list.txt
rm -f $CACHE_DIR/old_cubes.txt
rm -f $CACHE_DIR/cubes_all.txt