#!/usr/bin/env zsh
setopt null_glob

if [ "$1" != '' ]; then
    CUBE_ENV=$1
fi

if [ "$CUBE_ENV" = '' ]; then
    CUBE_ENV=joel
fi

CACHE_DIR=$(jq -r .$CUBE_ENV.cache_dir < cube_config.json)
PY="pdm run python"

echo "Refreshing local Scryfall cache"
${=PY} scryfall_cache.py

rm -f $CACHE_DIR/lists/*
echo "Downloading and generating reference list sheet"
${=PY} ref_list_gen.py $CUBE_ENV

rm -f $CACHE_DIR/card_reference.csv

rm -f cube_csv.log

echo "Processing and uniquing cube_raw.txt"

tr '\t' '\n' < $CACHE_DIR/cubes_raw.txt > $CACHE_DIR/cubes_all.txt
${=PY} unique.py < $CACHE_DIR/cubes_all.txt > $CACHE_DIR/old_cubes.txt

cat $CACHE_DIR/lists/* $CACHE_DIR/old_cubes.txt > $CACHE_DIR/all_cards.txt

echo "Creating cube_reference.csv"

${=PY} unique.py < $CACHE_DIR/all_cards.txt > $CACHE_DIR/card_list.txt
${=PY} create_cube_csv.py < $CACHE_DIR/card_list.txt > $CACHE_DIR/card_reference_tmp.csv
${=PY} unique.py < $CACHE_DIR/card_reference_tmp.csv > $CACHE_DIR/card_reference.csv

echo "Cleaning up..."

rm -f $CACHE_DIR/all_cards.txt
rm -f $CACHE_DIR/card_list.txt
rm -f $CACHE_DIR/old_cubes.txt
rm -f $CACHE_DIR/cubes_all.txt
rm -f $CACHE_DIR/card_reference_tmp.csv
