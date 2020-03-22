#!/usr/bin/env python3.6
# scryfall.py
# usage: python scryfall.py WAR > war.csv

import requests, time, logging, card_attrs, pymongo
from card_attrs import get_overrides

SEP_TYPE = 'Pipe'

API_URL = 'https://api.scryfall.com/cards'
CUBE_ATTRS = ['name', 'image_link', 'color_identity_name', 'type', 'cmc', 'subtypes', 'cube_sort_order']
SET_ATTRS = ['name_with_image_link', 'set_template_sort_order', 'color_identity_name', 'type', 'rarity', 'cmc', 'subtypes', 'power', 'toughness', 'oracle_one_line']

def get_attr_name(attr):
    map = {
        'cmc': 'CMC',
        'color_identity_name': 'Color Identity',
        'pt': 'P/T',
    }
    if attr in map:
        return map[attr]
    return attr.replace('_',' ').title()


def get_card_by_id(mtgo_id):
    client = pymongo.MongoClient()
    cards_en = client.scryfall.cards_en

    query = {
        '$or': [
            {'mtgo_id': int(mtgo_id)},
            {'mtgo_foil_id': int(mtgo_id)}
        ]
    }

    card = cards_en.find_one(query)

    if card is None:
        error_message = 'No match for card id {}'.format(mtgo_id)
        logging.error(error_message)

    return card


def get_card(card_name, set=None):
    client = pymongo.MongoClient()
    cards_en = client.scryfall.cards_en

    overrides = get_overrides()
    card_name = overrides['names'].get(card_name, card_name)

    query = {
        'name': card_name
    }

    if set is not None:
        query['set'] = set

    card = cards_en.find_one(query, sort=[('released_on', pymongo.ASCENDING)])

    if card is None:
        query = {
            'card_faces': {
                '$elemMatch': {
                    'name': card_name
                }
            }
        }
        if set is not None:
            query['set'] = set

        card = cards_en.find_one(query, sort=[('released_on', pymongo.ASCENDING)])

    if card is None:
        error_message = 'No match for card name {}'.format(card_name)
        if set is not None:
            error_message = error_message + ' and set {}'.format(set)
        logging.error(error_message)

    return(card)


def form_query(query_params):
    elements = ['{}:{}'.format(it[0], it[1]) for it in query_params.items()]
    return '+'.join(elements)


def get_set(set_code, additional_params={}, order='set'):
    query_params = {
        'e': set_code,
        'is': 'booster',
        '-t': 'basic',
    }

    query_params.update(additional_params)
    query= form_query(query_params)
    params = {'q': query}

    has_more=True
    cards = []
    url = '{}/search'.format(API_URL)

    while has_more:
        r = requests.get(url, params=params)
        time.sleep(.1)
        response = r.json()
        cards.extend(response['data'])

        has_more = response['has_more']

        if has_more:
            url=response['next_page']
            params={}

    return cards


def set_images(set_code, format='normal'):
    cards = get_set(set_code)
    tags = [card_attrs.image_tag_from_card(c, format=format) for c in cards]
    return ''.join(tags)


def card_attr_line(card_input, attrs):
    split = card_input.strip('\n').split('|')
    card_name = split[0].strip()

    if len(split) >= 2:
        set = split[1]
    else:
        set = None

    card = get_card(card_name, set=set)
    if card is None:
        card_attr_line = [card_name if (attr == 'name') else '' for attr in attrs]
    else:
        card_attr_line = [card_attrs.get_attr_fmt(card, attr) for attr in attrs]

    return(join_line(card_attr_line))


def join_line(line):
    if SEP_TYPE == 'Pipe':
        return('|'.join(line))
    if SEP_TYPE == 'Quotes and Comma':
        return('"' + '", "'.join(line) + '"')
    if SEP_TYPE == 'Tab':
        return('\t'.join(line))
