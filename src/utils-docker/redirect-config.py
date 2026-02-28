#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify
import json
import hashlib
from log import log;

log = log('/webcrate/log/app.log')
with open('/webcrate/redirects.yml', 'r') as f:
  content = f.read().strip()
  redirects = munchify(yaml.safe_load(content)) if content else {}
  f.close()

DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
UID_START_NUMBER = 100000
SSH_PORT_START_NUMBER = 10000

REDIRECT_NAME = sys.argv[1]

#cleanup configs
os.system(f'rm /webcrate/nginx/confs/redirect-{REDIRECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/core-confs/redirect-{REDIRECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/dnsmasq/hosts/redirect-{REDIRECT_NAME}.hosts > /dev/null 2>&1')
os.system(f'rm /webcrate/meta/redirects/redirect-{REDIRECT_NAME}.config > /dev/null 2>&1')

for redirectname,redirect in redirects.items():
  if REDIRECT_NAME == redirectname:
    dump = json.dumps(redirect, separators=(',', ':'), ensure_ascii=True)
    redirect.name = f'redirect-{redirectname}'
    if redirect.active:
      if redirect.https == 'letsencrypt':
        if os.path.isdir(f'/webcrate/letsencrypt/live/{redirect.name}'):
          with open(f'/webcrate/redirect-ssl.conf', 'r') as f:
            conf = f.read()
            f.close()
          conf = conf.replace('%type%', 'letsencrypt')
          conf = conf.replace('%path%', f'live/{redirect.name}')
          with open(f'/webcrate/nginx/ssl/{redirect.name}.conf', 'w') as f:
            f.write(conf)
            f.close()
          log.write(f'ssl config for {redirect.name} - generated', log.LEVEL.debug)

      if redirect.https == 'openssl':
        if os.path.isdir(f'/webcrate/openssl/{redirect.name}'):
          with open(f'/webcrate/redirect-ssl.conf', 'r') as f:
            conf = f.read()
            f.close()
          conf = conf.replace('%type%', 'openssl')
          conf = conf.replace('%path%', f'{redirect.name}')
          with open(f'/webcrate/nginx/ssl/{redirect.name}.conf', 'w') as f:
            f.write(conf)
            f.close()
          log.write(f'ssl config for {redirect.name} - generated', log.LEVEL.debug)

      conf = ''
      if os.path.isfile(f'/webcrate/nginx-templates/default-redirect.conf'):
        with open(f'/webcrate/nginx-templates/default-redirect.conf', 'r') as f:
          conf = f.read()
          f.close()

      conf = conf.replace('%redirect%', redirect.name)
      conf = conf.replace('%domains%', " ".join(redirect.domains))
      conf = conf.replace('%url%', redirect.url)

      with open(f'/webcrate/nginx/confs/{redirect.name}.conf', 'w') as f:
        f.write(conf)
        f.close()

      with open(f'/webcrate/nginx/core-confs/{redirect.name}.conf', 'w') as f:
        f.write(conf)
        f.close()

      log.write(f'nginx config for {redirect.name} - generated', log.LEVEL.debug)

      with open(f'/webcrate/dnsmasq/hosts/{redirect.name}.hosts', 'w') as f:
        f.write(f'{DOCKER_HOST_IP} {" ".join(redirect.domains)}\n')
        f.close()

    with open(f'/webcrate/meta/{redirect.name}.jsonDump', 'w') as f:
      f.write(dump)
      f.close()
    hash_object = hashlib.sha256(dump.encode())
    hex_dig = hash_object.hexdigest()
    os.system(f'printf "{hex_dig}" > /webcrate/meta/{redirect.name}.checksum')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/meta')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq')
sys.stdout.flush()
