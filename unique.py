#!/Users/joel/anaconda3/bin/python
# unique.py

import sys
s = {}
for line in sys.stdin:
  if line not in s:
    sys.stdout.write(line)
    s[line]=1
