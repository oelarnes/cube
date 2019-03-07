#!/usr/bin/env zsh

rm card_ref.txt
cat ./lists/* | python unique.py > card_ref.txt
