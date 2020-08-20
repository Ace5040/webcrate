#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()

SITES_PATH = '/sites'
WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
print(f'WEBCRATE_MODE = {WEBCRATE_MODE}')
if WEBCRATE_MODE == 'PRODUCTION':
  os.system(f'userdel dev > /dev/null 2>&1')
  for username,user in users.items():
    user.name = username
    os.system(f'groupadd --gid {user.uid} {user.name}')
    os.system(f'gpasswd -a nginx {user.name}')
    print(f'group {user.name} - added')

if WEBCRATE_MODE == 'DEV':
  os.system(f'groupadd --gid {WEBCRATE_GID} dev')
  os.system(f'gpasswd -a nginx dev')
  print(f'group dev - added')
