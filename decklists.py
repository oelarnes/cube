import pymongo
import os
import xml.etree.ElementTree as ET
import requests

from magic_data_utils.scryfall import get_card, get_card_by_id, get_attr

OUT_DIR = 'share'

XML_PRE = '''
<?xml version="1.0" encoding="utf-8"?>
<Deck xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NetDeckID>0</NetDeckID>
  <PreconstructedDeckID>0</PreconstructedDeckID>
'''

CARD_TEMPLATE = '<Cards CatID="{}" Quantity="1" Sideboard="false" Name="{}" />'

XML_POST = '</Deck>'

MTGO_LIST_DIR = 'mtgo_lists'
MTGO_LIST_COLLECTION = 'mtgo_lists'


def write_mtgo_collections():
    client = pymongo.MongoClient()
    collection = client.mtgo[MTGO_LIST_COLLECTION]

    for account in os.listdir(MTGO_LIST_DIR):
        if '.dek' in account:
            account_name = account.split('.')[0]
            card_ids = []
            root = ET.parse(os.path.join(MTGO_LIST_DIR, account)).getroot()
            for child in root:
                if child.tag == 'Cards':
                    card_ids.append(child.attrib['CatID'])
            collection.update_one({'account': account_name}, {'$set': {'list': card_ids}}, upsert=True)


def get_owned_cards_for_cube(cube_id, account="OCL_Sower", all_but=False):
    client = pymongo.MongoClient()
    collection = client.mtgo[MTGO_LIST_COLLECTION]
    cards = []
    missing = []

    text = requests.get(f'https://cubecobra.com/cube/download/plaintext/{cube_id}').text
    owned_cards = collection.find_one({'account': account})['list']
    owned_names = [get_attr(get_card_by_id(c), 'name') for c in owned_cards]
    for line in text.splitlines():
        card_name = get_attr(get_card(line), 'name')
        if card_name in owned_names:
            cards.append(card_name)
        else:
            missing.append(card_name)
    
    return missing if all_but else cards


def write_mtgo_txt(card_list, fileroot):
    filename = fileroot + '.mtgo'
    names = [get_attr(get_card(c), 'mtgo_name') for c in card_list]
    with open(os.path.join(OUT_DIR, filename), 'w') as outfile:
        outfile.writelines([f'1 {name}\n' for name in names])


def write_name_lines(card_list, fileroot):
    filename = fileroot + '.txt'
    names = [get_attr(get_card(c), 'name') for c in card_list]
    with open(os.path.join(OUT_DIR, filename), 'w') as outfile:
        outfile.writelines([f'{name}\n' for name in names])