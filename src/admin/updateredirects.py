#!/usr/bin/env python3

import os
import sys

with open('/webcrate/updated-redirects.yml', 'r') as updated:
  with open(f'/webcrate/redirects.yml', 'w') as redirectss:
      redirectss.write(updated.read())
      redirectss.close()
  updated.close()
os.system(f'rm /webcrate/updated-redirects.yml')
sys.exit(0)
