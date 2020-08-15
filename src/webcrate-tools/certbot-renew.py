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
LETSENCRYPT_EMAIL = os.environ.get('LETSENCRYPT_EMAIL', '')
active_certificate_exist = False

for username,user in users.items():
  user.name = username
  if user.https == 'letsencrypt':
    active_certificate_exist = True

if active_certificate_exist:
  print(f'run certbot renew')
  os.system(f'certbot renew --config-dir /webcrate/letsencrypt --deploy-hook /webcrate/certbot-renew-deploy.py');
