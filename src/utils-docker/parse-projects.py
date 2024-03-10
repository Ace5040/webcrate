#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

#cleanup configs
os.system(f'rm /webcrate/nginx/ssl/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/redirect/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/options/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/block/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/auth/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/gzip/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/confs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php_pools/* > /dev/null 2>&1')
os.system(f'rm /webcrate/dnsmasq/hosts/* > /dev/null 2>&1')
os.system(f'rm /webcrate/meta/projects/* > /dev/null 2>&1')

for projectname,project in projects.items():
  os.system(f'/project-config.py {projectname}')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/meta')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php_pools')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq')
sys.stdout.flush()
