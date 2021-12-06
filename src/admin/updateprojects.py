#!/usr/bin/env python3

import os
import sys

with open('/webcrate/updated-projects.yml', 'r') as updated:
  with open(f'/webcrate/projects.yml', 'w') as projects:
      projects.write(updated.read())
      projects.close()
  updated.close()
os.system(f'rm /webcrate/webcrate/updated-projects.yml')
sys.exit(0)
