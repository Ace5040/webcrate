#!/usr/bin/env python3

import os
import yaml
from munch import munchify

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

if WEBCRATE_MODE == 'PRODUCTION':
  for username,user in projects.items():
    user.name = username
    os.system(f'groupadd --gid {user.uid} {user.name}')
    os.system(f'gpasswd -a nginx {user.name}')
    print(f'group {user.name} - added')

if WEBCRATE_MODE == 'DEV':
  if WEBCRATE_GID != 0:
    os.system(f'groupadd --gid {WEBCRATE_GID} dev')
    os.system(f'gpasswd -a nginx dev')
    print(f'group dev - added')
  else:
    os.system(f'gpasswd -a nginx root')
    print(f'group root - added')
