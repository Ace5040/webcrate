#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify
import helpers
import time
from log import log;

log = log('/webcrate/log/app.log')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

with open('/webcrate/projects.yml', 'r') as f:
  content = f.read().strip()
  projects = munchify(yaml.safe_load(content)) if content else {}
  f.close()

PROJECT_NAME = sys.argv[1]
nginx_reload_needed = False

for projectname,project in projects.items():
  project.name = projectname
  if PROJECT_NAME == project.name:
    if project.active:
      if project.https == 'letsencrypt':
        domains = ",".join(list(filter(lambda domain: domain.split('.')[-1] != 'test', project.domains)))
        domains_prev = helpers.load_domains(project.name)
        if len(domains) and (domains != domains_prev or not os.path.isdir(f'/webcrate/letsencrypt/live/{project.name}') or not os.listdir(f'/webcrate/letsencrypt/live/{project.name}')):
          retries = 10
          while retries > 0 and not helpers.is_nginx_up():
            retries -= 1
            time.sleep(6)
          if retries > 0:
            with open(f'/webcrate/letsencrypt-meta/domains-{project.name}.txt', 'w') as f:
              f.write(domains)
              f.close()
            path = f'/webcrate/letsencrypt-meta/well-known/{project.name}'
            if not os.path.isdir(path):
              os.system(f'mkdir -p {path}')
            os.system(f'certbot certonly --key-type ecdsa --keep-until-expiring --renew-with-new-domains --allow-subset-of-names --config-dir /webcrate/letsencrypt --cert-name {project.name} --expand --webroot --webroot-path {path} -d {domains}')
            os.system(f'rm -rf {path}')
            log.write(f'{project.name} - letsencrypt certificate generated', log.LEVEL.debug)
            nginx_reload_needed = True

      if project.https == 'openssl':
        conf = helpers.genereate_openssl_conf(project.name, project.domains)
        conf_old = helpers.load_openssl_conf(project.name)
        if conf_old != conf or not os.path.exists(f'/webcrate/openssl/{project.name}/privkey.pem') or not os.path.exists(f'/webcrate/openssl/{project.name}/fullchain.pem'):
          os.system(f'mkdir -p /webcrate/openssl/{project.name}; rm /webcrate/openssl/{project.name}/*')
          with open(f'/webcrate/openssl/{project.name}/openssl.cnf', 'w') as f:
            f.write(conf)
            f.close()
          os.system(f'openssl genrsa -out /webcrate/openssl/{project.name}/privkey.pem 2048')
          os.system(f'openssl req -new -sha256 -key /webcrate/openssl/{project.name}/privkey.pem -out /webcrate/openssl/{project.name}/fullchain.csr -config /webcrate/openssl/{project.name}/openssl.cnf')
          os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/{project.name}/openssl.cnf -in /webcrate/openssl/{project.name}/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/{project.name}/fullchain.pem -days 5000 -sha256')
          log.write(f'{project.name} - openssl certificate generated', log.LEVEL.debug)
          nginx_reload_needed = True

      if project.https == 'openssl' or project.https == 'letsencrypt':
        if not os.path.exists(f'/webcrate/nginx/ssl/{project.name}.conf'):
          if (os.path.exists(f'/webcrate/openssl/{project.name}/privkey.pem') and os.path.exists(f'/webcrate/openssl/{project.name}/fullchain.pem')) or (os.path.isdir(f'/webcrate/letsencrypt/live/{project.name}') and os.listdir(f'/webcrate/letsencrypt/live/{project.name}')):
            with open(f'/webcrate/ssl.conf', 'r') as f:
              conf = f.read()
              f.close()
            conf = conf.replace('%type%', project.https)
            conf = conf.replace('%path%', f'{"live/" if project.https == "letsencrypt" else ""}{project.name}')
            with open(f'/webcrate/nginx/ssl/{project.name}.conf', 'w') as f:
              f.write(conf)
              f.close()
            log.write(f'{project.name} - ssl.conf generated', log.LEVEL.debug)
            nginx_reload_needed = True

      if project.https != 'disabled':
        if os.path.isdir(f'/webcrate/openssl/default'):
          with open(f'/webcrate/ssl.conf', 'r') as f:
            conf = f.read()
            f.close()
          conf = conf.replace('%type%', 'openssl')
          conf = conf.replace('%path%', 'default')
          with open(f'/webcrate/nginx/ssl/{project.name}-core.conf', 'w') as f:
            f.write(conf)
            f.close()
          log.write(f'ssl core config for {project.name} - generated', log.LEVEL.debug)

      if project.https == 'disabled' and os.path.exists(f'/webcrate/nginx/ssl/{project.name}.conf'):
        nginx_reload_needed = True
        os.system(f'rm /webcrate/nginx/ssl/{project.name}.conf')
        os.system(f'rm /webcrate/nginx/ssl/{project.name}-core.conf')
        log.write(f'{project.name} - ssl.conf removed', log.LEVEL.debug)

      # os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx')
      # os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
      # os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt-meta')
      # os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/openssl')
      # os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets')

print(nginx_reload_needed)
