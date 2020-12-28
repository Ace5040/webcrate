#!/usr/bin/env python3

import os
import yaml
from munch import munchify

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()

with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

any_letsencrypt_https_configs_found = False
for username,user in users.items():
  if user.https == 'letsencrypt':
    any_letsencrypt_https_configs_found = True
for servicename,service in services.items():
  if service.https == 'letsencrypt':
    any_letsencrypt_https_configs_found = True

if any_letsencrypt_https_configs_found:
  os.system(f'certbot renew --config-dir /webcrate/letsencrypt --deploy-hook /webcrate/certbot-renew-deploy.py');
