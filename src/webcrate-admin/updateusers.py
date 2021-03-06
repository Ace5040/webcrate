#!/usr/bin/env python3

import os
import sys

with open('/webcrate/updated-users.yml', 'r') as updated:
  with open(f'/webcrate/users.yml', 'w') as users:
      users.write(updated.read())
      users.close()
  updated.close()
os.system(f'rm /webcrate/webcrate/updated-users.yml')
sys.exit(0)
