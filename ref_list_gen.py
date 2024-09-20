import logging
import fnmatch
import os
import time
import sys
import json
from datetime import date

from cube_lists import download_cube_list
import magic_data_utils.scryfall as scryfall

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV = 'joel' if not sys.argv[:1] else sys.argv[1]

with open('cube_config.json') as config_file:
    config = json.load(config_file)[ENV]

CACHE_DIR = config['cache_dir']
LISTS = config['lists']

logging.basicConfig(filename='logs/ref_list_gen.log',level=logging.WARNING)

ENV_DIR = f'{ROOT_DIR}/{CACHE_DIR}'
LIST_DIR = f'{ENV_DIR}/lists'

OUT_FILE = f'{ENV_DIR}/ref_lists.csv'

REF_LIST_MAP = {
    "AlphaFrog": {
        'path_regex': 'AlphaFrogVintageCube*',
        'name': 'AlphaFrog Cube'
    }, 
    "kq": {
        'path_regex': '450VintageUnpowered*',
        'name': 'kq Unpowered Cube'
    },
    "dumbcards": {
        'path_regex': 'dumbcardstbh*',
        'name': 'dumb cards tbh'
    },
    "UsmanCube": {
        'path_regex': 'UsmansCube*',
        'name': "Usman's Cube",
    },
    "LSVCube": {
        "path_regex": "LSVCube*",
        'name': 'LSVCube',
    },
    "mengucube": {
        'path_regex': 'VintageMenguCube*',
        'name': 'Vintage MenguCube'
    },
    'ocl': {
        'path_regex': 'OCLCube*',
        'name': 'OCL Cube'
    },
    'ocli': {
        'path_regex': 'OCLInteractiveCube*',
        'name': 'OCL Interactive Cube'
    },
    'oclp': {
        'path_regex': 'OCLPoweredCube*',
        'name': 'OCL Powered Cube'
    },
    'oclmaster': {
        'path_regex': 'CubeMaster*',
        'name': 'Joel\'s Cube Master',
    },
    'oclcollection': {
        'path_regex': 'OCLOwned*',
        'name': 'OCL Owned Cards'
    },
    'joel': {
        'path_regex': 'JoelsCube*',
        'name': "Joel's Cube",
    },
    'modovintage': {
        'path_regex': 'MTGOVintageCube*',
        'name': 'MTGO Vintage Cube'
    },
    'ryan': {
        'path_regex': 'RyanSaxe*',
        'name': "Ryan's Cube"
    },
    'wtwlf123': {
        'path_regex': 'wtwlf123*',
        'name': "wtwlf123's Cube"
    },
    '450_powered': {
        'path_regex': 'Simple_Mans450Powered*',
        'name': "Simple Man's 450 Powered"
    },
    'dekkaru': {
        'path_regex': 'Dekkaru*',
        'name': "Dekkaru Cube"
    },
    'scgconcube': {
        'path_regex': 'SCGCON*',
        'name': 'SCG Con Cube',
    },
    'culticcube': {
        'path_regex': 'Eleusis*',
        'name': 'Eleusis'
    },
}
                                       
def get_file_match(filename):
    for file in os.listdir(LIST_DIR):
        if fnmatch.fnmatch(file, filename):
            return LIST_DIR + '/' + file


def cube_name(cube_id, date_str):
    link = 'https://cubecobra.com/cube/overview/{}'.format(cube_id)
    return '=HYPERLINK("{}","{} {}")'.format(link, REF_LIST_MAP[cube_id]['name'], date_str)
    

def main():
    lists = []
    date_str = date.today().strftime('%d%b%y')
    scryfall_client = scryfall.get_client()

    for cube_id in LISTS:
        filename = REF_LIST_MAP[cube_id]['path_regex']

        fn = get_file_match(filename)
        if fn is not None:
            os.remove(fn)

        download_cube_list(cube_id, LIST_DIR)
        time.sleep(1)
        fn = get_file_match(filename)
        if fn is None:
            logging.warning(
                'Download id {} failed to produce expected filename {}.'.format(cube_id, filename)
            )
            continue

        with open(fn, encoding='utf8') as f:
            lines0 = f.readlines()
            while True:
                time.sleep(2)
                f.seek(0)
                lines = f.readlines()
                if lines == lines0:
                    break
                logging.warning('Not finished downloading. Downloaded {} cards.'.format(len(lines)))
                lines0 = lines
                        
            logging.info(f'{cube_id} downloaded')

                       
            lines = [scryfall.card_attr_line(scryfall_client, line, ['name']) for line in lines]
            lines.insert(0, cube_name(cube_id, date_str))
            lists.append(lines)

        logging.info(
            f'{cube_id} processed as {filename}'
        )

    try:
        os.remove(OUT_FILE)
    except OSError:
        pass

    with open(OUT_FILE, 'a') as write_file:
        k = max([len(list_) for list_ in lists])

        for i in range(k):
            row = [list_[i] if len(list_) > i else '' for list_ in lists]
            write_file.write('|'.join(row)+'\n')

if __name__ == '__main__':
    main()
    