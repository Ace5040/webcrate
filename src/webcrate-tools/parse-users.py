#!/usr/bin/env python3

import os
import yaml
import time
from munch import munchify
from pprint import pprint

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()

SITES_PATH = '/sites'
WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
LETSENCRYPT_EMAIL = os.environ.get('LETSENCRYPT_EMAIL', '')
reload_needed = False

def is_mysql_up(host, password):
  return int(os.popen(f'mysql -u root -h {host} -p"{password}" -e "show databases;" | grep "Database" | wc -l').read().strip())

def is_postgresql_up(host, password):
  return os.popen(f'psql -d "host={host} user=postgres password={password}" -tAc "SELECT 1 FROM pg_database LIMIT 1;"').read().strip()

for username,user in users.items():
  user.name = username
  if user.mysql_db:
    mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1]
    retries = 10
    while retries > 0 and is_mysql_up('mysql', mysql_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql_database_found = int(os.popen(f'mysql -u root -h mysql -p"{mysql_root_password}" -e "show databases like \'{user.name}\';" | grep "Database ({user.name})" | wc -l').read().strip())
      if mysql_database_found == 0:
        mysql_user_password=os.popen(f"docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{user.name}-mysql.txt', 'w') as f:
          f.write(f'host=mysql\n')
          f.write(f'name={user.name}\n')
          f.write(f'user={user.name}\n')
          f.write(f'password={mysql_user_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{user.name}-mysql.txt')
        os.system(f'mysql -u root -h mysql -p"{mysql_root_password}" -e "CREATE DATABASE {user.name};"')
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"CREATE USER '{user.name}'@'%' IDENTIFIED BY \\\"{mysql_user_password}\\\";\"")
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON {user.name} . * TO '{user.name}'@'%';\"")
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql user {user.name} and db created')
      else:
        print(f'mysql user {user.name} and db already exists')

  if user.mysql5_db:
    mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("=")[1][1:][:-1]
    retries = 10
    while retries > 0 and is_mysql_up('mysql5', mysql5_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql5_database_found = int(os.popen(f'mysql -u root -h mysql5 -p"{mysql5_root_password}" -e "show databases like \'{user.name}\';" | grep "Database ({user.name})" | wc -l').read().strip())
      if mysql5_database_found == 0:
        mysql5_user_password=os.popen(f"docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{user.name}-mysql5.txt', 'w') as f:
          f.write(f'host=mysql\n')
          f.write(f'db={user.name}\n')
          f.write(f'user={user.name}\n')
          f.write(f'password={mysql5_user_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{user.name}-mysql5.txt')
        os.system(f'mysql -u root -h mysql5 -p"{mysql5_root_password}" -e "CREATE DATABASE {user.name};"')
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"CREATE USER '{user.name}'@'%' IDENTIFIED BY \\\"{mysql5_user_password}\\\";\"")
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"GRANT ALL PRIVILEGES ON {user.name} . * TO '{user.name}'@'%';\"")
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql5 user {user.name} and db created')
      else:
        print(f'mysql5 user {user.name} and db already exists')

  if user.postgresql_db:
    postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("=")[1][1:][:-1]
    retries = 10
    while retries > 0 and is_postgresql_up('postgres', postgres_root_password) == 1:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      postgres_database_found = os.popen(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'postgres\';"').read().strip()
      if postgres_database_found != 1:
        postgres_user_password=os.popen(f"docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{user.name}-postgres.txt', 'w') as f:
          f.write(f'host=postgres\n')
          f.write(f'db={user.name}\n')
          f.write(f'user={user.name}\n')
          f.write(f'password={postgres_user_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{user.name}-postgres.txt')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {user.name};"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE USER {user.name} WITH ENCRYPTED PASSWORD \'{postgres_user_password}\';"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {user.name} TO {user.name};"')
        print(f'postgresql user {user.name} and db created')
      else:
        print(f'postgresql user {user.name} and db already exists')

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
          os.system(f'chown -R {user.uid if WEBCRATE_MODE == "PRODUCTION" else WEBCRATE_UID}:{user.uid if WEBCRATE_MODE == "PRODUCTION" else WEBCRATE_UID} {SITES_PATH}/{user.name}/{user.root_folder.split("/")[0]}')
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
      os.system(f'rm /webcrate/ssl_configs/{user.name}.conf')
      print(f'ssl config for {user.name} - removed')
    print(f'ssl config for {user.name} - not present')

if reload_needed:
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
  print(f'changes detected - reloading nginx config')
  os.system(f'docker exec webcrate-nginx nginx -s reload')
