#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/users/users.yml') as f:
  users = munchify(yaml.safe_load(f))

SITES_PATH = '/sites'
MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
DEV_MODE_USER_UID = os.environ.get('DEV_MODE_USER_UID', '1000')
DEV_MODE_USER_GID = os.environ.get('DEV_MODE_USER_GID', '1000')
print(f'MODE = {MODE}')
if MODE == 'PRODUCTION':
  os.system(f'userdel dev > /dev/null 2>&1')
  for username,user in users.items():
    user.name = username
    os.system(f'groupadd --gid {user.uid} {user.name}')
    os.system(f'gpasswd -a nginx {user.name}')
    print(f'group {user.name} - added')

if MODE == 'DEV':
  os.system(f'groupadd --gid {DEV_MODE_USER_GID} dev')
  os.system(f'gpasswd -a nginx dev')
  print(f'group dev - added')
