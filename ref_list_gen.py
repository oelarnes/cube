import logging
import fnmatch
import os
import time
import sys
import json
from datetime import date

from cube_lists import download_cube_list, COBRA, TUTOR
import scryfall

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
    'ocl': {
        'path_regex': 'OCLCube*',
        'name': 'OCL Cube',
        'source': COBRA
    },
    'ocli': {
        'path_regex': 'OCLInteractiveCube*',
        'name': 'OCL Interactive Cube',
        'source': COBRA
    },
    'oclp': {
        'path_regex': 'OCLPoweredCube*',
        'name': 'OCL Powered Cube',
        'source': COBRA
    },
    'oclmaster': {
        'path_regex': 'CubeMaster*',
        'name': 'Joel\'s Cube Master',
        'source': COBRA
    },
    'joel': {
        'path_regex': 'JoelsCube*',
        'name': "Joel's Cube",
        'source': COBRA
    },
    14381: {
        'path_regex': 'hypercube*',
        'name': 'Hypercube',
        'source': TUTOR,
    },
    'modovintage': {
        'path_regex': 'ModoVintageCube*',
        'name': 'MTGO Vintage Cube',
        'source': COBRA
    },
    64542: {
        'path_regex': 'ryans_cube*',
        'name': "Ryan's Cube",
        'source': TUTOR
    },
    170: {
        'path_regex': 'wtwlf123s_cube*',
        'name': "wtwlf123's Cube",
        'source': TUTOR
    },
    127541: {
        'path_regex': 'usmans_cube*',
        'name': "Usman's Cube",
        'source': TUTOR,
    },
    56212: {
        'path_regex': 'aarons_450_cube*',
        'name': "Aaron's 450 Cube",
        'source': TUTOR
    },
    58025: {
        'path_regex': 'andys_sweet_synergy*',
        'name': "Andy's Sweet Synergy",
        'source': TUTOR
    },
    '450_powered': {
        'path_regex': 'Simple_Mans450Powered*',
        'name': "Simple Man's 450 Powered",
        'source': COBRA
    }
}

def get_file_match(filename):
    for file in os.listdir(LIST_DIR):
        if fnmatch.fnmatch(file, filename):
            return LIST_DIR + '/' + file


def cube_name(cube_id, source, date_str):
    if source==TUTOR:
        link = 'https://www.cubetutor.com/viewcube/{}'.format(cube_id)
    else:
        link = 'https://cubecobra.com/cube/overview/{}'.format(cube_id)
    return '=HYPERLINK("{}","{} {}")'.format(link, REF_LIST_MAP[cube_id]['name'], date_str)
    

def main():
    lists = []
    date_str = date.today().strftime('%d%b%y')

    for cube_id in LISTS:
        filename = REF_LIST_MAP[cube_id]['path_regex']
        source = REF_LIST_MAP[cube_id]['source']

        fn = get_file_match(filename)
        if fn is not None:
            os.remove(fn)

        download_cube_list(cube_id, LIST_DIR, source=source)
        time.sleep(1)
        fn = get_file_match(filename)
        if fn is None:
            logging.warning(
                'Download id {} failed to produce expected filename {}.'.format(cube_id, filename)
            )
            continue

        with open(fn) as f:
            lines0 = f.readlines()
            while True:
                time.sleep(5)
                f.seek(0)
                lines = f.readlines()
                if lines == lines0:
                    break
                logging.warning('Not finished downloading. Downloaded {} cards.'.format(len(lines)))
                lines0 = lines
            lines = [scryfall.card_attr_line(line, ['name']) for line in lines]
            lines.insert(0, cube_name(cube_id, source, date_str))
            lists.append(lines)

        logging.info(
            f'{cube_id} downloaded as {filename}'
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