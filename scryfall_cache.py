import requests
import time
import pymongo

API_URL = 'https://api.scryfall.com/cards'

def clear_cache():
    client = pymongo.MongoClient()
    client.scryfall.cards_en.delete_many({})

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
        data.extend(cards['data'])

    if len(lang):
        data = [card for card in data if card['lang'] == lang]

    return data

def populate_cache():
    clear_cache()
    cards = fetch_cards()

    client = pymongo.MongoClient()
    client.scryfall.cards_en.insert_many(cards)

    print('{} cards inserted', client.scryfall.cards_en.count_documents({}))
