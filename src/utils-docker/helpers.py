#!/usr/bin/env python3
import os
import yaml
from munch import munchify
from log import log
log = log('/webcrate/log/app.log')

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

def load_openssl_conf(name):
  conf_old = ''
  if os.path.isfile(f'/webcrate/openssl/{name}/openssl.cnf'):
    with open(f'/webcrate/openssl/{name}/openssl.cnf', 'r') as f:
      conf_old = f.read()
      f.close()
  return conf_old

def load_domains(name):
  domains = ''
  if os.path.isfile(f'/webcrate/letsencrypt-meta/domains-{name}.txt'):
    with open(f'/webcrate/letsencrypt-meta/domains-{name}.txt', 'r') as f:
      domains = f.read()
      f.close()
  return domains

def is_nginx_up():
  return "nginx is running" in os.popen(f'docker exec webcrate-nginx service nginx status').read().strip()

def is_mysql_up(host, password):
  return int(os.popen(f'mysql -u root -h {host} -p"{password}" -e "show databases;" 2>/dev/null | grep "Database" | wc -l').read().strip())

def is_postgresql_up(host, password):
  return os.popen(f'psql -d "host={host} user=postgres password={password}" -tAc "SELECT 1 FROM pg_database LIMIT 1;" 2>/dev/null').read().strip()

def is_container_exists(container_name):
  return os.popen(f'docker container inspect {container_name} 2>/dev/null | grep \\"/{container_name}\\" | wc -l').read().strip() == '1'

def is_network_exists(network_name):
  return os.popen(f'docker network inspect {network_name} 2>/dev/null | grep \\"{network_name}\\" | wc -l').read().strip() == '1'

def is_network_has_connection(network_name, container_name):
  return os.popen(f'docker network inspect {network_name} 2>/dev/null | grep \\"{container_name}\\" | wc -l').read().strip() == '1'

def genereate_openssl_conf(name, domains):
  countryName = os.environ.get('WEBCRATE_COUNTRY', '')
  organizationName = os.environ.get('WEBCRATE_ORGANIZATION', '')
  OPENSSL_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', '')
  return (f'[req]\n'
    f'distinguished_name = dn\n'
    f'prompt = no\n'
    f'req_extensions = SAN\n'
    f'[dn]\n'
    f'C={countryName}\n'
    f'O={organizationName}\n'
    f'emailAddress={OPENSSL_EMAIL}\n'
    f'CN = {name}\n'
    f'[SAN]\n'
    f'subjectAltName = DNS:{",DNS:".join(domains)}\n')

def genereate_openssl_root_conf():
  countryName = os.environ.get('WEBCRATE_COUNTRY', '')
  OPENSSL_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', '')
  return (f'[req]\n'
    f'distinguished_name = dn\n'
    f'prompt = no\n'
    f'x509_extensions = x509_ext\n'
    f'[dn]\n'
    f'C={countryName}\n'
    f'O=Webcrate\n'
    f'emailAddress={OPENSSL_EMAIL}\n'
    f'CN = Webcrate\n'
    f'[ x509_ext ]\n'
    f'subjectKeyIdentifier = hash\n'
    f'authorityKeyIdentifier = keyid:always,issuer\n'
    f'basicConstraints = critical, CA:TRUE\n'
    f'keyUsage = critical, digitalSignature, keyEncipherment, cRLSign, keyCertSign\n'
    f'extendedKeyUsage = serverAuth\n')

def init_openssl_root_conf():
  countryName = os.environ.get('WEBCRATE_COUNTRY', '')
  OPENSSL_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', '')
  nginx_reload_needed = False
  openssl_root_conf_changed = False
  #load pervious openssl root config
  openssl_root_conf_prev = ''
  if os.path.isfile(f'/webcrate/secrets/openssl-root.cnf'):
    with open(f'/webcrate/secrets/openssl-root.cnf', 'r') as f:
      openssl_root_conf_prev = f.read()
      f.close()
  #generate openssl root config
  openssl_root_conf = (f'[req]\n'
  f'prompt = no\n'
  f'distinguished_name = dn\n'
  f'x509_extensions = x509_ext\n'
  f'[ dn ]\n'
  f'C={countryName}\n'
  f'O=Webcrate\n'
  f'emailAddress={OPENSSL_EMAIL}\n'
  f'CN = Webcrate\n'
  f'[ x509_ext ]\n'
  f'subjectKeyIdentifier = hash\n'
  f'authorityKeyIdentifier = keyid:always,issuer\n'
  f'basicConstraints = critical, CA:TRUE\n'
  f'keyUsage = critical, digitalSignature, keyEncipherment, cRLSign, keyCertSign\n'
  #f'subjectAltName = DNS:test.com\n'
  f'extendedKeyUsage = serverAuth\n')

  if openssl_root_conf_prev != openssl_root_conf or not os.path.isfile(f'/webcrate/secrets/rootCA.crt'):
    openssl_root_conf_changed = True
    log.write(f'openssl root config changed', log.LEVEL.debug)
    os.system(f'rm -f /webcrate/secrets/rootCA.key; rm -f /webcrate/secrets/rootCA.crt; rm -f /webcrate/secrets/rootCA.srl; rm -f /webcrate/secrets/openssl-root.cnf')
    os.system(f'openssl genrsa -out /webcrate/secrets/rootCA.key 4096')
    with open(f'/webcrate/secrets/openssl-root.cnf', 'w') as f:
      f.write(openssl_root_conf)
      f.close()
    os.system(f'openssl req -x509 -new -nodes -key /webcrate/secrets/rootCA.key -sha256 -days 825 -out /webcrate/secrets/rootCA.crt -config /webcrate/secrets/openssl-root.cnf')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/rootCA.key')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/rootCA.crt')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/openssl-root.cnf')

  if openssl_root_conf_changed:
    if os.path.exists(f'/webcrate/openssl') and os.listdir(f'/webcrate/openssl'):
      os.system(f'rm -r /webcrate/openssl/*')

  conf = genereate_openssl_conf('default', ['default'])
  conf_old = load_openssl_conf('default')
  if conf_old != conf or not os.path.exists(f'/webcrate/openssl/default/privkey.pem') or not os.path.exists(f'/webcrate/openssl/default/fullchain.pem'):
    os.system(f'mkdir -p /webcrate/openssl/default')
    if os.listdir(f'/webcrate/openssl/default'):
      os.system(f'rm /webcrate/openssl/default/*')
    with open(f'/webcrate/openssl/default/openssl.cnf', 'w') as f:
      f.write(conf)
      f.close()
    os.system(f'openssl genrsa -out /webcrate/openssl/default/privkey.pem 2048')
    os.system(f'openssl req -new -sha256 -key /webcrate/openssl/default/privkey.pem -out /webcrate/openssl/default/fullchain.csr -config /webcrate/openssl/default/openssl.cnf')
    os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/default/openssl.cnf -in /webcrate/openssl/default/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/default/fullchain.pem -days 5000 -sha256')
    os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/openssl/default')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/rootCA.srl')
    nginx_reload_needed = True
  return nginx_reload_needed

def init_letsencrypt_conf():
  LETSENCRYPT_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', '')
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
    LETSENCRYPT_EMAIL_prev = ''
    if os.path.isfile('/webcrate/letsencrypt-meta/letsencrypt-email.txt'):
      with open('/webcrate/letsencrypt-meta/letsencrypt-email.txt', 'r') as f:
        LETSENCRYPT_EMAIL_prev = f.read()
        f.close()
    if LETSENCRYPT_EMAIL_prev != LETSENCRYPT_EMAIL:
      if os.path.exists(f'/webcrate/letsencrypt') and os.listdir(f'/webcrate/letsencrypt'):
        os.system(f'rm -r /webcrate/letsencrypt/*')
      if os.path.exists(f'/webcrate/letsencrypt-meta') and os.listdir(f'/webcrate/letsencrypt-meta'):
        os.system(f'rm -r /webcrate/letsencrypt-meta/*')
      with open('/webcrate/letsencrypt-meta/letsencrypt-email.txt', 'w') as f:
        f.write(LETSENCRYPT_EMAIL)
        f.close()
    if not os.path.isdir('/webcrate/letsencrypt/accounts/acme-v02.api.letsencrypt.org/directory') or not os.listdir('/webcrate/letsencrypt/accounts/acme-v02.api.letsencrypt.org/directory'):
      os.system(f'certbot register --config-dir /webcrate/letsencrypt --agree-tos --eff-email --email {LETSENCRYPT_EMAIL}')
