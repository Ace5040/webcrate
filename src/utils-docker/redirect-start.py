#!/usr/bin/env python3

import os
import sys
import yaml
import idna
import helpers
import asyncio
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/redirects.yml', 'r') as f:
  redirects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
WEBCRATE_PWD = os.environ.get('WEBCRATE_PWD', '')
REDIRECT_NAME = sys.argv[1]

async def initCertificates (redirect):
  nginx_reload_needed = False
  if redirect.https == 'letsencrypt':
    domains = ",".join(list(filter(lambda domain: domain.split('.')[-1] != 'test', redirect.domains)))
    domains_prev = helpers.load_domains(redirect.name)
    if len(domains) and (domains != domains_prev or not os.path.isdir(f'/webcrate/letsencrypt/live/{redirect.name}') or not os.listdir(f'/webcrate/letsencrypt/live/{redirect.name}')):
      retries = 30
      while retries > 0 and not helpers.is_nginx_up():
        retries -= 1
        await asyncio.sleep(2)
      if retries > 0:
        with open(f'/webcrate/letsencrypt-meta/domains-{redirect.name}.txt', 'w') as f:
          f.write(domains)
          f.close()
        path = f'/webcrate/letsencrypt-meta/well-known/{redirect.name}'
        if not os.path.isdir(path):
          os.system(f'mkdir -p {path}')
        os.system(f'certbot certonly --key-type ecdsa --keep-until-expiring --renew-with-new-domains --allow-subset-of-names --config-dir /webcrate/letsencrypt --cert-name {redirect.name} --expand --webroot --webroot-path {path} -d {domains}')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
        os.system(f'rm -rf {path}')
        log.write(f'{redirect.name} - letsencrypt certificate generated', log.LEVEL.debug)
        nginx_reload_needed = True

  if redirect.https == 'openssl':
    conf = helpers.genereate_openssl_conf(redirect.name, redirect.domains)
    conf_old = helpers.load_openssl_conf(redirect.name)
    if conf_old != conf or not os.path.exists(f'/webcrate/openssl/{redirect.name}/privkey.pem') or not os.path.exists(f'/webcrate/openssl/{redirect.name}/fullchain.pem'):
      os.system(f'mkdir -p /webcrate/openssl/{redirect.name}')
      if os.listdir(f'/webcrate/openssl/{redirect.name}'):
        os.system(f'rm /webcrate/openssl/{redirect.name}/*')
      with open(f'/webcrate/openssl/{redirect.name}/openssl.cnf', 'w') as f:
        f.write(conf)
        f.close()
      os.system(f'openssl genrsa -out /webcrate/openssl/{redirect.name}/privkey.pem 2048')
      os.system(f'openssl req -new -sha256 -key /webcrate/openssl/{redirect.name}/privkey.pem -out /webcrate/openssl/{redirect.name}/fullchain.csr -config /webcrate/openssl/{redirect.name}/openssl.cnf')
      os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/{redirect.name}/openssl.cnf -in /webcrate/openssl/{redirect.name}/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/{redirect.name}/fullchain.pem -days 5000 -sha256')
      os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/openssl/{redirect.name}')
      nginx_reload_needed = True
      log.write(f'{redirect.name} - openssl certificate generated', log.LEVEL.debug)

  if redirect.https == 'openssl' or redirect.https == 'letsencrypt':
    if not os.path.exists(f'/webcrate/nginx/ssl/{redirect.name}.conf'):
      if (
          os.path.exists(f'/webcrate/openssl/{redirect.name}/privkey.pem')
          and
          os.path.exists(f'/webcrate/openssl/{redirect.name}/fullchain.pem')
        ) or (
          os.path.isdir(f'/webcrate/letsencrypt/live/{redirect.name}')
          and
          os.listdir(f'/webcrate/letsencrypt/live/{redirect.name}')
        ):
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', redirect.https)
        conf = conf.replace('%path%', f'{"live/" if redirect.https == "letsencrypt" else ""}{redirect.name}')
        with open(f'/webcrate/nginx/ssl/{redirect.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        log.write(f'{redirect.name} - ssl.conf generated', log.LEVEL.debug)
        nginx_reload_needed = True

  if redirect.https == 'disabled' and os.path.exists(f'/webcrate/nginx/ssl/{redirect.name}.conf'):
    nginx_reload_needed = True
    os.system(f'rm /webcrate/nginx/ssl/{redirect.name}.conf')
    log.write(f'{redirect.name} - ssl.conf removed', log.LEVEL.debug)
  return nginx_reload_needed

async def asyncOps (redirect):
  initCertificatesTask = asyncio.create_task(initCertificates(redirect))
  await initCertificatesTask
  return initCertificatesTask.result()

for redirectname,redirect in redirects.items():
  if REDIRECT_NAME == redirectname and redirect.active:
    redirect.name = f'redirect-{redirectname}'
    nginx_reload_needed = asyncio.run(asyncOps(redirect))
    if nginx_reload_needed:
      os.system(f'docker exec webcrate-nginx nginx -s reload')
      log.write(f'{redirect.name} - changes detected - nginx config reloaded', log.LEVEL.debug)

    log.write(f'{redirect.name} - started', log.LEVEL.debug)

sys.stdout.flush()
sys.exit(0)
