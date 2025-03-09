#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint
from log import log;

log = log('/webcrate/log/app.log')
with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))

DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

WEBCRATE_SERVICE_HTMLTOPDF = os.environ.get('WEBCRATE_SERVICE_HTMLTOPDF', 'false') == 'true'
WEBCRATE_SERVICE_DOCTOHTML = os.environ.get('WEBCRATE_SERVICE_DOCTOHTML', 'false') == 'true'
WEBCRATE_SERVICE_STATS = os.environ.get('WEBCRATE_SERVICE_STATS', 'false') == 'true'

for servicename, service in services.items():
  if  ( servicename != 'doctohtml' or WEBCRATE_SERVICE_DOCTOHTML ) and \
      ( servicename != 'htmltopdf' or WEBCRATE_SERVICE_HTMLTOPDF ) and \
      ( servicename != 'grafana' or WEBCRATE_SERVICE_STATS ):

    service.name = servicename

    template = 'default';
    if os.path.isfile(f'/webcrate/nginx-templates/{service.name}-service.conf'):
      template = service.name
    os.system(f'cp -rf /webcrate/nginx-templates/{template}-service.conf /webcrate/nginx/confs/{service.name}-service.conf')

    with open(f'/webcrate/nginx/confs/{service.name}-service.conf', 'r') as f:
      conf = f.read()
      f.close()

    conf = conf.replace('%domain%', service.domain)
    conf = conf.replace('%host%', f'webcrate-{service.name}')
    conf = conf.replace('%service%', service.name)
    conf = conf.replace('%port%', str(service.port))

    with open(f'/webcrate/nginx/confs/{service.name}-service.conf', 'w') as f:
      f.write(conf)
      f.close()

    with open(f'/webcrate/nginx/core-confs/{service.name}-service.conf', 'w') as f:
      f.write(conf)
      f.close()

    log.write(f'{service.name} config - generated', log.LEVEL.debug)

    if service.https == 'letsencrypt':
      if os.path.isdir(f'/webcrate/letsencrypt/live/{service.name}'):
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', 'letsencrypt')
        conf = conf.replace('%path%', f'live/{service.name}')
        with open(f'/webcrate/nginx/ssl/{service.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        log.write(f'ssl config for {service.name} - generated', log.LEVEL.debug)
    if service.https == 'openssl':
      if os.path.isdir(f'/webcrate/openssl/{service.name}'):
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', 'openssl')
        conf = conf.replace('%path%', service.name)
        with open(f'/webcrate/nginx/ssl/{service.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        log.write(f'ssl config for {service.name} - generated', log.LEVEL.debug)
    with open(f'/webcrate/dnsmasq/hosts/{service.name}.hosts', 'w') as f:
      f.write(f'{DOCKER_HOST_IP} {service.domain}\n')
      f.close()

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx/confs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq')
