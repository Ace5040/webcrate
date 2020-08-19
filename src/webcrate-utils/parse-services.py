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

print(f'WEBCRATE_MODE = {WEBCRATE_MODE}')

for servicename, service in services.items():
  service.name = servicename

  os.system(f'cp -rf /webcrate/nginx-templates/{service.name if service.nginx_config == "custom" else "default-service"}.conf /webcrate/nginx_configs/{service.name}.conf')

  with open(f'/webcrate/nginx_configs/{service.name}.conf', 'r') as f:
    conf = f.read()
    f.close()

  conf = conf.replace('%domains%', " ".join(service.domains))
  conf = conf.replace('%host%', service.name)
  conf = conf.replace('%port%', str(service.port))

  with open(f'/webcrate/nginx_configs/{service.name}.conf', 'w') as f:
    f.write(conf)
    f.close()

  print(f'{service.name} config - generated')

if WEBCRATE_MODE == "DEV":
  with open(f'/webcrate/dnsmasq_hosts/hosts_nginx', 'a') as f:
    for servicename, service in services.items():
      service.name = servicename
      f.write(f'{DOCKER_HOST_IP} {" ".join(service.domains)}\n')
    f.close()

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq_hosts')