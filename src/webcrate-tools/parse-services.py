#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

for servicename, service in services.items():
  service.name = servicename
  template = 'default';
  if os.path.isfile(f'/webcrate/nginx-templates/{service.name}-service.conf'):
    template = service.name
  os.system(f'cp -rf /webcrate/nginx-templates/{template}-service.conf /webcrate/nginx_configs/{service.name}-service.conf')

  with open(f'/webcrate/nginx_configs/{service.name}-service.conf', 'r') as f:
    conf = f.read()
    f.close()

  conf = conf.replace('%domain%', service.domain)
  conf = conf.replace('%host%', service.name)
  conf = conf.replace('%service%', service.name)
  conf = conf.replace('%port%', str(service.port))

  with open(f'/webcrate/nginx_configs/{service.name}-service.conf', 'w') as f:
    f.write(conf)
    f.close()

  print(f'{service.name} config - generated')

  if service.https == 'letsencrypt':
    if os.path.isdir(f'/webcrate/letsencrypt/live/{service.name}'):
      with open(f'/webcrate/ssl.conf', 'r') as f:
        conf = f.read()
        f.close()
      conf = conf.replace('%type%', 'letsencrypt')
      conf = conf.replace('%path%', f'live/{service.name}')
      with open(f'/webcrate/ssl_configs/{service.name}.conf', 'w') as f:
        f.write(conf)
        f.close()
      print(f'ssl config for {service.name} - generated')
  if service.https == 'openssl':
    if os.path.isdir(f'/webcrate/openssl/{service.name}'):
      with open(f'/webcrate/ssl.conf', 'r') as f:
        conf = f.read()
        f.close()
      conf = conf.replace('%type%', 'openssl')
      conf = conf.replace('%path%', service.name)
      with open(f'/webcrate/ssl_configs/{service.name}.conf', 'w') as f:
        f.write(conf)
        f.close()
      print(f'ssl config for {service.name} - generated')

if WEBCRATE_MODE == "DEV":
  with open(f'/webcrate-dnsmasq/config/hosts_nginx', 'a') as f:
    for servicename, service in services.items():
      service.name = servicename
      f.write(f'{DOCKER_HOST_IP} {service.domain}\n')
    f.close()

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate-dnsmasq/config')
