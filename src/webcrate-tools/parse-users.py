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
reload_needed = False

for username,user in users.items():
  user.name = username
  if user.https == 'letsencrypt':
    if not os.path.isdir(f'/webcrate/letsencrypt/accounts'):
      print(f'certbot register --config-dir /webcrate/letsencrypt --agree-tos --eff-email --email {LETSENCRYPT_EMAIL}')
      output = os.popen(f'certbot register --config-dir /webcrate/letsencrypt --agree-tos --eff-email --email {LETSENCRYPT_EMAIL}').read()
      print(output)
      reload_needed = True
    if os.path.isdir(f'/webcrate/letsencrypt/live/{user.name}'):
      print(f'certificate for {user.name} - already exists')
      if not os.path.exists(f'/webcrate/ssl_configs/{user.name}.conf'):
        reload_needed = True
    else:
      path = f'{SITES_PATH}/{user.name}/{user.root_folder}'
      domains = list(filter(lambda domain: domain.split('.')[-1] != 'test', user.domains))
      if len(domains):
        if not os.path.isdir(path):
          os.system(f'mkdir -p {path}')
          os.system(f'chown -R {user.uid if MODE == "PRODUCTION" else DEV_MODE_USER_UID}:{user.uid if MODE == "PRODUCTION" else DEV_MODE_USER_UID} {SITES_PATH}/{user.name}/{user.root_folder.split("/")[0]}')
        print(path)
        print(f'certbot certonly --config-dir /webcrate/letsencrypt --cert-path /webcrate/letsencrypt --cert-name {user.name} --expand --webroot --webroot-path {path} -d {",".join(domains)}')
        output = os.popen(f'certbot certonly --config-dir /webcrate/letsencrypt --cert-name {user.name} --expand --webroot --webroot-path {path} -d {",".join(domains)}').read()
        print(output)
        print(f'certificate for {user.name} - generated')
        reload_needed = True
    if not os.path.exists(f'/webcrate/ssl_configs/{user.name}.conf'):
      with open(f'/webcrate/ssl.conf', 'r') as f:
        conf = f.read()
        f.close()
      conf = conf.replace('%user%', user.name)
      with open(f'/webcrate/ssl_configs/{user.name}.conf', 'w') as f:
        f.write(conf)
        f.close()
      print(f'ssl config for {user.name} - generated')
    else:
      print(f'ssl config for {user.name} - already exists')
  else:
    if os.path.exists(f'/webcrate/ssl_configs/{user.name}.conf'):
      reload_needed = True
      os.system(f'rm /webcrate/ssl_configs/{user.name}.conf');
      print(f'ssl config for {user.name} - removed')
    print(f'ssl config for {user.name} - not present')

if reload_needed:
  print(f'changes detected - reloading nginx config')
  os.system(f'docker exec webcrate-nginx nginx -s reload');
