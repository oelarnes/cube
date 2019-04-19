from cube_tutor import download_cube_list
import logging
import fnmatch
import os
import time
import scryfall

logging.basicConfig(filename='ref_list_gen.log',level=logging.WARNING)

DIR = './lists'
REF_LISTS = {
    64141: 'joels_cube.txt',
    134850: 'jamess_cube.txt',
    5936: 'mtgo_vintage_cube*',
    64542: 'ryans_cube.txt',
    170: 'wtwlf123s_cube.txt',
    127541: 'usmans_cube.txt',
    56212: 'aarons_450_cube.txt',
    58025: 'andys_sweet_synergy_540.txt',
    804: 'rasgueos_cube.txt',
    3710: 'simple_mans_450_powered.txt'
}
OUT_FILE = 'ref_lists.csv'

lists = []

def get_file_match(filename):
    for file in os.listdir(DIR):
        if fnmatch.fnmatch(file, filename):
            return DIR + '/' + file


for id, filename in REF_LISTS.items():
    fn = get_file_match(filename)
    if fn is not None:
        os.remove(fn)

    download_cube_list(id, DIR)
    time.sleep(1)
    fn = get_file_match(filename)
    if fn is None:
        logging.warning(
            'Download id {} failed to produce expected filename {}.'.format(id, filename)
        )

    else:
        f = open(fn)
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
        lines.insert(0, filename.split('.')[0])
        lists.append(lines)


try:
    os.remove(OUT_FILE)
except OSError:
    pass

write_file = open(OUT_FILE, 'a')

k = max([len(list) for list in lists])

for i in range(k):
    row = [list[i] if len(list) > i else '' for list in lists]
    write_file.write('|'.join(row)+'\n')

write_file.close()
