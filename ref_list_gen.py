from cube_tutor import download_cube_list
import logging
import fnmatch
import os

logging.basicConfig(filename='ref_list_gen.log',level=logging.WARNING)

DIR = './lists'
REF_LISTS = {
    64141: 'joels_cube.txt',
    134850: 'jamess_cube.txt',
    5936, 'mtgo_vintage_cube*',
    64542, 'ryans_cube.txt',
    170, 'wtwlf123s_cube.txt',
    127541, 'usmans_cube.txt',
    56212, 'aarons_450_cube.txt',
    58025, 'andys_sweet_synergy_540.txt',
    804, 'rasgueos_cube.txt',
    3710, 'simple_mans_450_powered.txt'
}

lists = []

def get_file_match(filename):
    for file in os.listdir(DIR):
        if fnmatch.fnmatch(file, filename):
            return DIR + '/' + file


for id, filename in REF_LISTS.items():
    if (fn=get_file_match(filename)) is not None:
        os.remove(fn)

    download_cube_list(id, DIR)
    time.sleep(1)
    fn = get_file_match(filename)
    if fn is None:
        logging.WARNING(
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
        lines.insert(0, fn.split('.')[0])
        lists &= lines

k = max([len(list) for list in lists])

for i in range(k):
