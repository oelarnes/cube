import logging
import os
import sys
import json
from datetime import date

from cube_lists import download_cube_list, get_cube_name
from scryfall import Scryfall

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV = sys.argv[1] if len(sys.argv) > 1 else 'joel'

with open('cube_config.json') as config_file:
    config = json.load(config_file)[ENV]

CACHE_DIR = config['cache_dir']
LISTS = config['lists']

os.makedirs(f'{ROOT_DIR}/logs', exist_ok=True)
logging.basicConfig(filename=f'{ROOT_DIR}/logs/ref_list_gen.log', level=logging.WARNING)

ENV_DIR = f'{ROOT_DIR}/{CACHE_DIR}'
LIST_DIR = f'{ENV_DIR}/lists'

OUT_FILE = f'{ENV_DIR}/ref_lists.csv'

os.makedirs(LIST_DIR, exist_ok=True)

def cube_name(cube_id, date_str):
    link = 'https://cubecobra.com/cube/overview/{}'.format(cube_id)
    return '=HYPERLINK("{}","{} {}")'.format(link, get_cube_name(cube_id), date_str)


def main():
    lists = []
    date_str = date.today().strftime('%d%b%y')
    scryfall_client = Scryfall()

    for cube_id in LISTS:
        try:
            fn = download_cube_list(cube_id, LIST_DIR)
        except Exception as e:
            logging.warning('Download id {} failed: {}'.format(cube_id, e))
            continue

        with open(fn, encoding='utf8') as f:
            lines = [line for line in f.readlines() if line.strip()]

            logging.info(f'{cube_id} downloaded')

            names = [scryfall_client.get_card(line.strip()).name for line in lines]
            unique_names = list(dict.fromkeys(names))
            unique_names.insert(0, cube_name(cube_id, date_str))
            lists.append(unique_names)

        logging.info(
            f'{cube_id} processed as {fn}'
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
    