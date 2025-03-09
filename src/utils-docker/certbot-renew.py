#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

any_letsencrypt_https_configs_found = False
for projectname,project in projects.items():
  if project.https == 'letsencrypt':
    any_letsencrypt_https_configs_found = True
for servicename,service in services.items():
  if service.https == 'letsencrypt':
    any_letsencrypt_https_configs_found = True

if any_letsencrypt_https_configs_found:
  WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
  WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
  log.write(f'Run certbot renew script', log.LEVEL.debug)
  os.system(f'certbot renew --key-type ecdsa --config-dir /webcrate/letsencrypt --deploy-hook /certbot-renew-deploy.py');
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
else:
  log.write(f'No letsencrypt configs found', log.LEVEL.debug)
