#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify

with open('/webcrate/redirects.yml', 'r') as f:
  redirects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

#cleanup configs
# os.system(f'rm /webcrate/nginx/ssl/* > /dev/null 2>&1')
# os.system(f'rm /webcrate/dnsmasq/hosts/* > /dev/null 2>&1')
os.system(f'rm /webcrate/meta/redirects/* > /dev/null 2>&1')

for redirectname,redirect in redirects.items():
  os.system(f'/redirect-config.py {redirectname}')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/meta')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq')
sys.stdout.flush()
