import re
import json
from functools import lru_cache

COLOR_NAME_MAP = {
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

RARITY_ORDER = [
    'common',
    'uncommon',
    'rare',
    'mythic'
]

COLOR_IDENTITY_NAME_ORDER = list(COLOR_NAME_MAP.values())

TYPE_ORDER = [
    "Creature",
    "Artifact Creature",
    "Enchantment Creature",
    "Planeswalker",
    "Instant",
    "Sorcery",
    "Artifact",
    "Enchantment",
    "Enchantment Artifact",
    "Land",
]

SET_TEMPLATE_RANK = ['rarity_rank', 'color_identity_rank', 'type_rank', 'cmc', 'name']
CUBE_RANK = ['color_identity_rank', 'type_rank', 'cmc', 'name']

@lru_cache(maxsize=1)
def get_overrides():
    with open('cache/overrides.json') as overrides:
        return json.load(overrides)


def sort_order_string(rank_list):
    # if string, keep as is. if double, convert to 2 digit string, if
    def convert_el(el):
        if type(el) == type(1):
            return '{:02d}'.format(el)
        if type(el) == type(1.0):
            return '{:02.0f}'.format(el)
        return str(el)

    return ''.join([convert_el(el) for el in rank_list])


def rank_by_order(attr, order):
    return order.index(attr) if attr in order else len(order) + 1


def image_formula_from_card(card, format='normal'):
    return '=IMAGE("{}", 3)'.format(card['image_uris'][format])


def clean_oracle_text(text):
    text = text.replace('\n', '; ')
    reminder_text_re = r'\(.*?\)'
    return re.sub(reminder_text_re, '', text)


def shorten_oracle_text(text, to_length=64):
    text = clean_oracle_text(text)

    if len(text) > to_length:
        text = text[:to_length-3]+"..."
    return text


def strip_supertype(type_line):
    supertypes = ['Basic', 'Legendary', 'Ongoing', 'Snow', 'World']
    for type in supertypes:
        type_line = type_line.replace(type + ' ', '')
    return(type_line)


def image_tag_from_card(card, format='normal'):
    return '<img src={}></img>'.format(card['image_uris'][format])


def format_attr(attr):
    if type(attr)== type([]):
        return(''.join(attr))
    return str(attr)


def name_with_image_link(card):
    name = get_attr(card, 'name')
    image_link = get_attr(card, 'image_link')

    return '=HYPERLINK("{}","{}")'.format(image_link, name)


def mtgo_name(card):
    if 'card_faces' in card and card['layout'] == 'split':
        names = [card['card_faces'][i]['name'] for i in [0,1]]
        return '/'.join(names)
    return get_attr(card, 'name')


def get_attr(card, attr):
    card = dict(card)
    overrides = get_overrides()['attrs']
    if attr != 'name' and attr in overrides.get(get_attr(card, 'name'), {}):
        return overrides[get_attr(card, 'name')][attr]

    # take some attributes from the front face including name
    if 'card_faces' in card:
        front = dict(card['card_faces'][0])
        if card['layout'] in ('transform', 'flip', 'adventure'):
            card['name'] = front['name']
        front.update(card)
        card = front

    if attr == 'type':
        type_line = card['type_line']
        type_line = strip_supertype(type_line)
        return type_line.split(' — ')[0].split(' // ')[0]
    if attr == 'subtypes':
        if '—' in card['type_line']:
            return card['type_line'].split(' — ')[1].split(' // ')[0]
        else:
            return ''
    if attr == 'color_identity_name':
        col_id = format_attr(get_attr(card, 'color_identity'))
        if col_id in COLOR_NAME_MAP:
            return COLOR_NAME_MAP[format_attr(get_attr(card, 'color_identity'))]
        return col_id
    if attr == 'image_tag':
        return image_tag_from_card(card)
    if attr == 'image_formula':
        return image_formula_from_card(card)
    if attr == 'image_link':
        return card['image_uris']['large']
    if attr == 'oracle_one_line':
        return clean_oracle_text(get_attr(card, 'oracle_text'))
    if attr == 'short_oracle':
        return shorten_oracle_text(get_attr(card, 'oracle_text'))
    if attr == 'pt':
        if 'power' in card and 'toughness' in card:
            return '{}/{}'.format(card['power'], card['toughness'])
    if attr == 'type_rank':
        return rank_by_order(get_attr(card, 'type'), TYPE_ORDER)
    if attr == 'color_identity_rank':
        return rank_by_order(
            get_attr(card, 'color_identity_name'),
            COLOR_IDENTITY_NAME_ORDER
        )
    if attr == 'rarity_rank':
        return rank_by_order(
            get_attr(card, 'rarity'),
            RARITY_ORDER
        )
    if attr == 'set_template_sort_order':
        return sort_order_string([
            get_attr(card, rank_attr) for rank_attr in SET_TEMPLATE_RANK
        ])
    if attr == 'cube_sort_order':
        return sort_order_string([
            get_attr(card, rank_attr) for rank_attr in CUBE_RANK
        ])
    if attr == 'name_with_image_link':
        return name_with_image_link(card)
    if attr == 'mtgo_name':
        return mtgo_name(card)
    if attr in card:
        return card[attr]
    return ''


def get_attr_fmt(card, attr):
    return format_attr(get_attr(card, attr))
