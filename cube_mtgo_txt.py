#!/Users/joel/anaconda3/bin/python
# create_cube_dek.py

from cube_tutor import download_cube_list
import scryfall, time, logging

CUBE_ID = 135529
CUBE_FILENAME = 'ocl_cube.txt'
DEK_FILENAME = 'ocl_cube.dek'
DIR = './share'

logging.basicConfig(filename='cube_dek.log',level=logging.WARNING)

download_cube_list(CUBE_ID, DIR)

f = open('/'.join([DIR, CUBE_FILENAME]))

time.sleep(1)
lines0 = f.readlines()
while True:
    time.sleep(5)
    f.seek(0)
    lines = f.readlines()
    if lines == lines0:
        break
    logging.warning('Not finished downloading. Downloaded {} cards.'.format(len(lines)))
    lines0 = lines

out = open('/'.join([DIR, DEK_FILENAME]), 'w')
out.writelines(['1 {}\n'.format(scryfall.card_attr_line(line, ['mtgo_name'])) for line in lines])
out.close()
