import logging
import fnmatch
import os
import time
import sys
import json
from datetime import date

from cube_tutor import download_cube_list
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
    64141: {
        'path_regex': 'joels_cube*',
        'name': "Joel's Cube"
    },
    135529: {
        'path_regex': "ocl_cube*",
        'name': "OCL Cube"
    },
    14381: {
        'path_regex': 'hypercube*',
        'name': 'Hypercube'
    },
    5936: {
        'path_regex': 'mtgo_vintage_cube*',
        'name': 'MTGO Vintage Cube'
    },
    64542: {
        'path_regex': 'ryans_cube*',
        'name': "Ryan's Cube"
    },
    170: {
        'path_regex': 'wtwlf123s_cube*',
        'name': "wtwlf123's Cube"
    },
    127541: {
        'path_regex': 'usmans_cube*',
        'name': "Usman's Cube"
    },
    56212: {
        'path_regex': 'aarons_450_cube*',
        'name': "Aaron's 450 Cube"
    },
    58025: {
        'path_regex': 'andys_sweet_synergy*',
        'name': "Andy's Sweet Synergy"
    },
    3710: {
        'path_regex': 'simple_mans_450_powered*',
        'name': "Simple Man's 450 Powered"
    }
}

def get_file_match(filename):
    for file in os.listdir(LIST_DIR):
        if fnmatch.fnmatch(file, filename):
            return LIST_DIR + '/' + file


def cube_name(cube_id, date_str):
    link = 'https://www.cubetutor.com/viewcube/{}'.format(cube_id)
    return '=HYPERLINK("{}","{} {}")'.format(link, REF_LIST_MAP[cube_id]['name'], date_str)


def main():
    lists = []
    date_str = date.today().strftime('%d%b%y')

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
            lines.insert(0, cube_name(cube_id, date_str))
            lists.append(lines)

        logging.info(
            f'{cube_name(cube_id, date_str)} downloaded as {filename}'
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