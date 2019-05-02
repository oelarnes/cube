#!/Users/joel/anaconda3/bin/python
# unique.py

import sys
s = {'\n'}
for line in sys.stdin:
  line = line.lstrip().rstrip() + '\n'
  if line not in s:
    sys.stdout.write(line)
    s.add(line)