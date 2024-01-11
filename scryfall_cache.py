import datetime

import requests
import pymongo

API_URL = 'https://api.scryfall.com/bulk-data/default_cards'

def clear_cache():
    client = pymongo.MongoClient()
    deleted = client.scryfall.cards_en.delete_many({})
    print(f'{deleted.deleted_count} cards deleted')

def fetch_cards(lang='en'):
    bulk_data_result = requests.get(API_URL)
    download_uri = bulk_data_result.json()['download_uri']

    download = requests.get(download_uri)
    cards = download.json()
    
    print('{} pulled'.format(len(cards)))

    return cards

def populate_cache():
    cards = fetch_cards()

    client = pymongo.MongoClient()
    clear_cache()
    client.scryfall.cards_en.insert_many(cards)
    client.scryfall.cards_en.create_index('mtgo_id')
    client.scryfall.cards_en.create_index('name')
    client.scryfall.import_metadata.update_one(
        {}, 
        {   
            '$set': {
                'as_of': f'{datetime.datetime.utcnow().isoformat(timespec="milliseconds")}Z'
            }
        }, 
        upsert=True
    )

    print(f'{client.scryfall.cards_en.count_documents({})} cards inserted')

if __name__ == '__main__':
    populate_cache()
