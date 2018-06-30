#!/usr/bin/env python3.6
# scryfall.py

import requests, time

SEP_TYPE = 'Pipe'

color_name_map = {
    "W":    "White",
    "U":    "Blue",
    "B":    "Black",
    "R":    "Red",
    "G":    "Green",
    "UW":   "Azorius",
    "BU":   "Dimir",
    "BR":   "Rakdos",
    "GR":   "Gruul",
    "GW":   "Selesnya",
    'BW':   "Orzhov",
    "BG":   "Golgari",
    "GU":   "Simic",
    "RU":   "Izzet",
    "RW":   "Boros",
    "BUW":  "Esper",
    "BRU":  "Grixis",
    "BGR":  "Jund",
    "GRW":  "Naya",
    "GUW":  "Bant",
    "BGW":  "Abzan",
    "BGU":  "Sultai",
    "GRU":  "Temur",
    "RUW":  "Jeskai",
    "BRW":  "Mardu",
    "BGRUW":    "Five-Color",
    "":     "Colorless",
}

def get_card(card_name, exact=True):
    query_type = 'exact' if exact else 'fuzzy'
    card_name = card_name.replace(' ', '+')
    r = requests.get('https://api.scryfall.com/cards/named?{}={}'.format(query_type, card_name))
    time.sleep(.1) # rate limit by request
    return(r.json())

def card_attr_line(card_name, *argv):
    card = get_card(card_name)
    attrs = [format_attr(get_attr(card, attr)) for attr in argv]

    return(join_line(attrs))

def join_line(line):
    if SEP_TYPE == 'Pipe':
        return('|'.join(line))
    if SEP_TYPE == 'Quotes and Comma':
        return('"' + '", "'.join(line) + '"')
    if SEP_TYPE == 'Tab':
        return('\t'.join(line))

def strip_supertype(type_line):
    supertypes = ['Basic', 'Legendary', 'Ongoing', 'Snow', 'World']
    for type in supertypes:
        type_line = type_line.replace(type + ' ', '')
    return(type_line)

def get_attr(card, attr):
    if attr == 'type':
        type_line = card['type_line']
        type_line = strip_supertype(type_line)
        return(type_line.split(' — ')[0].split(' // ')[0])
    if attr == 'subtypes':
        if '—' in card['type_line']:
            return(card['type_line'].split(' — ')[1].split(' // ')[0])
        else:
            return('')
    if attr == 'color_identity_name':
        return(color_name_map[format_attr(card['color_identity'])])
    return(card[attr])

def format_attr(attr):
    if type(attr)== type([]):
        return(''.join(attr))
    return(str(attr))

def get_info_line(card_name):
    return card_attr_line(card_name, 'name', 'color_identity_name', 'type', 'cmc', 'subtypes')
