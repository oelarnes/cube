#!/usr/bin/env python3.6
# scryfall.py

import requests, time, logging, card_attrs, scryfall_cache

logging.basicConfig(level=logging.DEBUG)

SEP_TYPE = 'Pipe'

API_URL = 'https://api.scryfall.com/cards'

CUBE_ATTRS = ['name', 'image_link', 'color_identity_name', 'type', 'cmc', 'subtypes']
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


def get_card(card_name, exact=True, set=None):
    query_type = 'exact' if exact else 'fuzzy'

    params = {
        query_type: card_name
    }
    if set is not None:
        params['set'] = set
    r = requests.get('{}/named'.format(API_URL), params=params)
    time.sleep(.1) # rate limit by request
    card = r.json()

    # take some attributes from the front face including name
    if 'card_faces' in card:
        front = card['card_faces'][0]
        if card['layout'] == 'transform':
            card['name'] = front['name']
        front.update(card)
        card = front

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

    query = form_query(query_params)
    params = {
        'order': order,
        'q': query
    }

    params_str = '&'.join([
        '{}={}'.format(it[0], it[1]) for it in params.items()
    ])

    url = '{}/search'.format(API_URL)

    has_more=True
    cards = []

    while has_more:
        r = requests.get(url, params=params_str)
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
    card_name = split[0]
    if len(split) >= 2:
        set = split[1]
    else:
        set = None

    card = get_card(card_name, set=set)
    card_attr_line = [card_attrs.get_attr_fmt(card, attr) for attr in attrs]

    return(join_line(card_attr_line))


def join_line(line):
    if SEP_TYPE == 'Pipe':
        return('|'.join(line))
    if SEP_TYPE == 'Quotes and Comma':
        return('"' + '", "'.join(line) + '"')
    if SEP_TYPE == 'Tab':
        return('\t'.join(line))
