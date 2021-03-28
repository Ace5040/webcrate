#!/usr/bin/env python3

import os
import yaml
import time
from munch import munchify

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()
with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
countryName = os.environ.get('WEBCRATE_countryName', '')
organizationName = os.environ.get('WEBCRATE_organizationName', '')
LETSENCRYPT_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', '')
OPENSSL_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', '')

def genereate_openssl_conf(name, domains, countryName, organizationName, OPENSSL_EMAIL):
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

def is_mysql_up(host, password):
  return int(os.popen(f'mysql -u root -h {host} -p"{password}" -e "show databases;" | grep "Database" | wc -l').read().strip())

def is_postgresql_up(host, password):
  return os.popen(f'psql -d "host={host} user=postgres password={password}" -tAc "SELECT 1 FROM pg_database LIMIT 1;"').read().strip()

nginx_reload_needed = False
openssl_root_conf_changed = False

any_letsencrypt_https_configs_found = False
for username,user in users.items():
  if user.https == 'letsencrypt':
    any_letsencrypt_https_configs_found = True
for servicename,service in services.items():
  if service.https == 'letsencrypt':
    any_letsencrypt_https_configs_found = True

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
f'[ dn ]\n'
f'C={countryName}\n'
f'O=Webcrate\n'
f'emailAddress={OPENSSL_EMAIL}\n'
f'CN = Webcrate\n')

if openssl_root_conf_prev != openssl_root_conf:
  openssl_root_conf_changed = True
  print(f'openssl root config changed')
  os.system(f'rm -f /webcrate/secrets/rootCA.key; rm -f /webcrate/secrets/rootCA.crt; rm -f /webcrate/secrets/rootCA.srl; rm -f /webcrate/secrets/openssl-root.cnf')
  os.system(f'openssl genrsa -out /webcrate/secrets/rootCA.key 4096')
  with open(f'/webcrate/secrets/openssl-root.cnf', 'w') as f:
    f.write(openssl_root_conf)
    f.close()
  os.system(f'openssl req -x509 -new -nodes -key /webcrate/secrets/rootCA.key -sha256 -days 10000 -out /webcrate/secrets/rootCA.crt -config /webcrate/secrets/openssl-root.cnf')

if openssl_root_conf_changed:
  os.system(f'rm -r /webcrate/openssl/default')
conf = genereate_openssl_conf('default', ['default'], countryName, organizationName, OPENSSL_EMAIL)
conf_old = load_openssl_conf('default')
if conf_old != conf or not os.path.exists(f'/webcrate/openssl/default/privkey.pem') or not os.path.exists(f'/webcrate/openssl/default/fullchain.pem'):
  os.system(f'mkdir -p /webcrate/openssl/default; rm /webcrate/openssl/default/*')
  with open(f'/webcrate/openssl/default/openssl.cnf', 'w') as f:
    f.write(conf)
    f.close()
  os.system(f'openssl genrsa -out /webcrate/openssl/default/privkey.pem 2048')
  os.system(f'openssl req -new -sha256 -key /webcrate/openssl/default/privkey.pem -out /webcrate/openssl/default/fullchain.csr -config /webcrate/openssl/default/openssl.cnf')
  os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/default/openssl.cnf -in /webcrate/openssl/default/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/default/fullchain.pem -days 5000 -sha256')
  nginx_reload_needed = True

if any_letsencrypt_https_configs_found:

  LETSENCRYPT_EMAIL_prev = ''
  if os.path.isfile('/webcrate/letsencrypt-meta/letsencrypt-email.txt'):
    with open('/webcrate/letsencrypt-meta/letsencrypt-email.txt', 'r') as f:
      LETSENCRYPT_EMAIL_prev = f.read()
      f.close()
  if LETSENCRYPT_EMAIL_prev != LETSENCRYPT_EMAIL:
    os.system('rm -r /webcrate/letsencrypt/*')
    os.system('rm -r /webcrate/letsencrypt-meta/*')
    with open('/webcrate/letsencrypt-meta/letsencrypt-email.txt', 'w') as f:
      f.write(LETSENCRYPT_EMAIL)
      f.close()
  if not os.path.isdir('/webcrate/letsencrypt/accounts/acme-v02.api.letsencrypt.org/directory') or not os.listdir('/webcrate/letsencrypt/accounts/acme-v02.api.letsencrypt.org/directory'):
    os.system(f'certbot register --config-dir /webcrate/letsencrypt --agree-tos --eff-email --email {LETSENCRYPT_EMAIL}')

#parse users
for username,user in users.items():
  user.name = username
  UID = user.uid
  GID = user.uid

  if WEBCRATE_MODE == 'DEV':
    UID = WEBCRATE_UID
    GID = WEBCRATE_GID

  if hasattr(user, 'volume'):
    user.folder = f'/projects{(user.volume + 1) if user.volume else ""}/{user.name}'
  else:
    user.folder = f'/projects/{user.name}'

  if user.mysql_db:
    mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and is_mysql_up('mysql', mysql_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql_database_found = int(os.popen(f'mysql -u root -h mysql -p"{mysql_root_password}" -e "show databases like \'{user.name}\';" | grep "Database ({user.name})" | wc -l').read().strip())
      if mysql_database_found == 0:
        mysql_user_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{user.name}-mysql.txt', 'w') as f:
          f.write(f'host=mysql\n')
          f.write(f'name={user.name}\n')
          f.write(f'user={user.name}\n')
          f.write(f'password={mysql_user_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{user.name}-mysql.txt')
        os.system(f'cp /webcrate/secrets/{user.name}-mysql.txt {user.folder}/mysql.txt')
        os.system(f'chown {UID}:{GID} {user.folder}/mysql.txt')
        os.system(f'chmod a-rwx,u+rw {user.folder}/mysql.txt')
        os.system(f'mysql -u root -h mysql -p"{mysql_root_password}" -e "CREATE DATABASE \`{user.name}\`;"')
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"CREATE USER \`{user.name}\`@'%' IDENTIFIED BY \\\"{mysql_user_password}\\\";\"")
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{user.name}\` . * TO \`{user.name}\`@'%';\"")
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql user {user.name} and db created')
      else:
        print(f'mysql user {user.name} and db already exists')

  if user.mysql5_db:
    mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and is_mysql_up('mysql5', mysql5_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql5_database_found = int(os.popen(f'mysql -u root -h mysql5 -p"{mysql5_root_password}" -e "show databases like \'{user.name}\';" | grep "Database ({user.name})" | wc -l').read().strip())
      if mysql5_database_found == 0:
        mysql5_user_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{user.name}-mysql5.txt', 'w') as f:
          f.write(f'host=mysql\n')
          f.write(f'db={user.name}\n')
          f.write(f'user={user.name}\n')
          f.write(f'password={mysql5_user_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{user.name}-mysql5.txt')
        os.system(f'cp /webcrate/secrets/{user.name}-mysql5.txt {user.folder}/mysql5.txt')
        os.system(f'chown {UID}:{GID} {user.folder}/mysql5.txt')
        os.system(f'chmod a-rwx,u+rw {user.folder}/mysql5.txt')
        os.system(f'mysql -u root -h mysql5 -p"{mysql5_root_password}" -e "CREATE DATABASE \`{user.name}\`;"')
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"CREATE USER \`{user.name}\`@'%' IDENTIFIED BY \\\"{mysql5_user_password}\\\";\"")
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{user.name}\` . * TO \`{user.name}\`@'%';\"")
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql5 user {user.name} and db created')
      else:
        print(f'mysql5 user {user.name} and db already exists')

  if user.postgresql_db:
    postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and is_postgresql_up('postgres', postgres_root_password) != '1':
      retries -= 1
      time.sleep(5)
    if retries > 0:
      postgres_database_found = os.popen(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'{user.name}\';"').read().strip()
      if postgres_database_found != '1':
        postgres_user_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{user.name}-postgres.txt', 'w') as f:
          f.write(f'host=postgres\n')
          f.write(f'db={user.name}\n')
          f.write(f'user={user.name}\n')
          f.write(f'password={postgres_user_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{user.name}-postgres.txt')
        os.system(f'cp /webcrate/secrets/{user.name}-postgres.txt {user.folder}/postgres.txt')
        os.system(f'chown {UID}:{GID} {user.folder}/postgres.txt')
        os.system(f'chmod a-rwx,u+rw {user.folder}/postgres.txt')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {user.name};"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE USER {user.name} WITH ENCRYPTED PASSWORD \'{postgres_user_password}\';"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {user.name} TO {user.name};"')
        print(f'postgresql user {user.name} and db created')
      else:
        print(f'postgresql user {user.name} and db already exists')

  if user.https == 'letsencrypt':
    domains = ",".join(list(filter(lambda domain: domain.split('.')[-1] != 'test', user.domains)))
    domains_prev = load_domains(user.name)
    if ( domains != domains_prev or not os.path.isdir(f'/webcrate/letsencrypt/live/{user.name}') or not os.listdir(f'/webcrate/letsencrypt/live/{user.name}')) and len(domains):
      with open(f'/webcrate/letsencrypt-meta/domains-{user.name}.txt', 'w') as f:
        f.write(domains)
        f.close()
      path = f'/webcrate/letsencrypt-meta/well-known/{user.name}'
      if not os.path.isdir(path):
        os.system(f'mkdir -p {path}')
      os.system(f'certbot certonly --keep-until-expiring --renew-with-new-domains --allow-subset-of-names --config-dir /webcrate/letsencrypt --cert-name {user.name} --expand --webroot --webroot-path {path} -d {domains}')
      print(f'certificate for {user.name} - generated')
      nginx_reload_needed = True

  if user.https == 'openssl':
    if openssl_root_conf_changed:
      os.system(f'rm -r /webcrate/openssl/{user.name}')
    conf = genereate_openssl_conf(user.name, user.domains, countryName, organizationName, OPENSSL_EMAIL)
    conf_old = load_openssl_conf(user.name)
    if conf_old != conf or not os.path.exists(f'/webcrate/openssl/{user.name}/privkey.pem') or not os.path.exists(f'/webcrate/openssl/{user.name}/fullchain.pem'):
      os.system(f'mkdir -p /webcrate/openssl/{user.name}; rm /webcrate/openssl/{user.name}/*')
      with open(f'/webcrate/openssl/{user.name}/openssl.cnf', 'w') as f:
        f.write(conf)
        f.close()
      os.system(f'openssl genrsa -out /webcrate/openssl/{user.name}/privkey.pem 2048')
      os.system(f'openssl req -new -sha256 -key /webcrate/openssl/{user.name}/privkey.pem -out /webcrate/openssl/{user.name}/fullchain.csr -config /webcrate/openssl/{user.name}/openssl.cnf')
      os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/{user.name}/openssl.cnf -in /webcrate/openssl/{user.name}/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/{user.name}/fullchain.pem -days 5000 -sha256')
      nginx_reload_needed = True

  if user.https == 'openssl' or user.https == 'letsencrypt':
    if not os.path.exists(f'/webcrate/ssl_configs/{user.name}.conf'):
      if (os.path.exists(f'/webcrate/openssl/{user.name}/privkey.pem') and os.path.exists(f'/webcrate/openssl/{user.name}/fullchain.pem')) or (os.path.isdir(f'/webcrate/letsencrypt/live/{user.name}') and os.listdir(f'/webcrate/letsencrypt/live/{user.name}')):
        nginx_reload_needed = True
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', user.https)
        conf = conf.replace('%path%', f'{"live/" if user.https == "letsencrypt" else ""}{user.name}')
        with open(f'/webcrate/ssl_configs/{user.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        print(f'ssl config for {user.name} - generated')

  if user.https == 'disabled' and os.path.exists(f'/webcrate/ssl_configs/{user.name}.conf'):
    nginx_reload_needed = True
    os.system(f'rm /webcrate/ssl_configs/{user.name}.conf')
    print(f'ssl config for {user.name} - removed')

#parse services
for servicename,service in services.items():
  service.name = servicename

  if service.mysql_db:
    mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and is_mysql_up('mysql', mysql_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql_database_found = int(os.popen(f'mysql -u root -h mysql -p"{mysql_root_password}" -e "show databases like \'{service.name}\';" | grep "Database ({service.name})" | wc -l').read().strip())
      if mysql_database_found == 0:
        mysql_service_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{service.name}-service-mysql.txt', 'w') as f:
          f.write(f'host=mysql\n')
          f.write(f'name={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={mysql_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-mysql.txt')
        os.system(f'mysql -u root -h mysql -p"{mysql_root_password}" -e "CREATE DATABASE \`{service.name}\`;"')
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"CREATE USER \`{service.name}\`@'%' IDENTIFIED BY \\\"{mysql_service_password}\\\";\"")
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{service.name}\` . * TO \`{service.name}\`@'%';\"")
        os.system(f"mysql -u root -h mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql user {service.name} and db created')
      else:
        print(f'mysql user {service.name} and db already exists')

  if service.mysql5_db:
    mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and is_mysql_up('mysql5', mysql5_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql5_database_found = int(os.popen(f'mysql -u root -h mysql5 -p"{mysql5_root_password}" -e "show databases like \'{service.name}\';" | grep "Database ({service.name})" | wc -l').read().strip())
      if mysql5_database_found == 0:
        mysql5_service_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{service.name}-service-mysql5.txt', 'w') as f:
          f.write(f'host=mysql\n')
          f.write(f'db={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={mysql5_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-mysql5.txt')
        os.system(f'mysql -u root -h mysql5 -p"{mysql5_root_password}" -e "CREATE DATABASE \`{service.name}\`;"')
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"CREATE USER \`{service.name}\`@'%' IDENTIFIED BY \\\"{mysql5_service_password}\\\";\"")
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{service.name}\` . * TO \`{service.name}\`@'%';\"")
        os.system(f"mysql -u root -h mysql5 -p\"{mysql5_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql5 user {service.name} and db created')
      else:
        print(f'mysql5 user {service.name} and db already exists')

  if service.postgresql_db:
    postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and is_postgresql_up('postgres', postgres_root_password) != '1':
      retries -= 1
      time.sleep(5)
    if retries > 0:
      postgres_database_found = os.popen(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'{service.name}\';"').read().strip()
      if postgres_database_found != '1':
        postgres_service_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{service.name}-service-postgres.txt', 'w') as f:
          f.write(f'host=postgres\n')
          f.write(f'db={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={postgres_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-postgres.txt')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {service.name} ENCODING \'UTF8\' TEMPLATE template0 LC_COLLATE=\'C\' LC_CTYPE=\'C\';"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE USER {service.name} WITH ENCRYPTED PASSWORD \'{postgres_service_password}\';"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {service.name} TO {service.name};"')
        print(f'postgresql user {service.name} and db created')
      else:
        print(f'postgresql user {service.name} and db already exists')

  if service.https == 'letsencrypt':
    domain = service.domain if service.domain.split('.')[-1] != 'test' else ''
    domain_prev = load_domains(service.name)
    if ( domain != domain_prev or not os.path.isdir(f'/webcrate/letsencrypt/live/{service.name}') or not os.listdir(f'/webcrate/letsencrypt/live/{service.name}')) and domain != '':
      with open(f'/webcrate/letsencrypt-meta/domains-{service.name}.txt', 'w') as f:
        f.write(domain)
        f.close()
      path = f'/webcrate/letsencrypt-meta/well-known/{service.name}'
      if not os.path.isdir(path):
        os.system(f'mkdir -p {path}')
      os.system(f'certbot certonly --keep-until-expiring --renew-with-new-domains --allow-subset-of-names --config-dir /webcrate/letsencrypt --cert-name {service.name} --expand --webroot --webroot-path {path} -d {domain}')
      print(f'certificate for {service.name} - generated')
      nginx_reload_needed = True

  if service.https == 'openssl':
    if openssl_root_conf_changed:
      os.system(f'rm -r /webcrate/openssl/{service.name}')
    conf = genereate_openssl_conf(service.name, [service.domain], countryName, organizationName, OPENSSL_EMAIL)
    conf_old = load_openssl_conf(service.name)
    if conf_old != conf or not os.path.exists(f'/webcrate/openssl/{service.name}/privkey.pem') or not os.path.exists(f'/webcrate/openssl/{service.name}/fullchain.pem'):
      os.system(f'mkdir -p /webcrate/openssl/{service.name}; rm /webcrate/openssl/{service.name}/*')
      with open(f'/webcrate/openssl/{service.name}/openssl.cnf', 'w') as f:
        f.write(conf)
        f.close()
      os.system(f'openssl genrsa -out /webcrate/openssl/{service.name}/privkey.pem 2048')
      os.system(f'openssl req -new -sha256 -key /webcrate/openssl/{service.name}/privkey.pem -out /webcrate/openssl/{service.name}/fullchain.csr -config /webcrate/openssl/{service.name}/openssl.cnf')
      os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/{service.name}/openssl.cnf -in /webcrate/openssl/{service.name}/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/{service.name}/fullchain.pem -days 5000 -sha256')
      nginx_reload_needed = True

  if service.https == 'openssl' or service.https == 'letsencrypt':
    if not os.path.exists(f'/webcrate/ssl_configs/{service.name}.conf'):
      if (os.path.exists(f'/webcrate/openssl/{service.name}/privkey.pem') and os.path.exists(f'/webcrate/openssl/{service.name}/fullchain.pem')) or (os.path.isdir(f'/webcrate/letsencrypt/live/{service.name}') and os.listdir(f'/webcrate/letsencrypt/live/{service.name}')):
        nginx_reload_needed = True
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', service.https)
        conf = conf.replace('%path%', f'{"live/" if service.https == "letsencrypt" else ""}{service.name}')
        with open(f'/webcrate/ssl_configs/{service.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        print(f'ssl config for {service.name} - generated')

  if service.https == 'disabled' and os.path.exists(f'/webcrate/ssl_configs/{service.name}.conf'):
    nginx_reload_needed = True
    os.system(f'rm /webcrate/ssl_configs/{service.name}.conf')
    print(f'ssl config for {service.name} - removed')

#reload nginx config if needed
if nginx_reload_needed:
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt-meta')
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/openssl')
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets')
  print(f'changes detected - reloading nginx config')
  os.system(f'docker exec webcrate-nginx nginx -s reload')
