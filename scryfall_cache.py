import time

import requests
import pymongo

API_URL = 'https://api.scryfall.com/cards'

def clear_cache():
    client = pymongo.MongoClient()
    deleted = client.scryfall.cards_en.delete_many({})
    print(deleted.deleted_count, ' cards deleted')

def fetch_cards(lang='en'):
    clear_cache()
    data = []

    next_page = API_URL
    has_more = True
    
    while has_more:
        r = requests.get(next_page)
        time.sleep(.1) # rate limit by request
        cards = r.json()
        has_more = cards['has_more']
        next_page = cards['next_page']

        data.extend([card for card in cards['data'] if not lang or card['lang'] == lang])
        print('{} pulled'.format(len(data)))

    return data

def populate_cache():
    clear_cache()
    cards = fetch_cards()

    client = pymongo.MongoClient()
    client.scryfall.cards_en.insert_many(cards)

    print(f'{client.scryfall.cards_en.count_documents({})} cards inserted')
