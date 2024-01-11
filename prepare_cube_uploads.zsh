#!/usr/bin/env zsh
if [ "$1" != '' ]; then
    CUBE_ENV=$1
fi

if [ "$CUBE_ENV" = '' ]; then
    CUBE_ENV=joel
fi

CACHE_DIR=$(jq -r .$CUBE_ENV.cache_dir < cube_config.json)

# python scryfall_cache.py

# echo "Downloading and generating reference list sheet\n"
# python ref_list_gen.py $CUBE_ENV

rm -f $CACHE_DIR/card_reference.csv

echo "Processing and uniquing cube_raw.txt\n"

tr '\t' '\n' < $CACHE_DIR/cubes_raw.txt > $CACHE_DIR/cubes_all.txt
python unique.py < $CACHE_DIR/cubes_all.txt > $CACHE_DIR/old_cubes.txt

cat $CACHE_DIR/lists/* $CACHE_DIR/old_cubes.txt > $CACHE_DIR/all_cards.txt

echo "Creating cube_reference.csv"

python unique.py < $CACHE_DIR/all_cards.txt > $CACHE_DIR/card_list.txt
python create_cube_csv.py < $CACHE_DIR/card_list.txt > $CACHE_DIR/card_reference_tmp.csv
python unique.py < $CACHE_DIR/card_reference_tmp.csv > $CACHE_DIR/card_reference.csv

echo "Cleaning up..."

rm -f $CACHE_DIR/all_cards.txt
rm -f $CACHE_DIR/card_list.txt
rm -f $CACHE_DIR/old_cubes.txt
rm -f $CACHE_DIR/cubes_all.txt
rm -f $CACHE_DIR/card_reference_tmp.csv
