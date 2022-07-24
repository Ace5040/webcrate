#!/usr/bin/env python3

import os
import yaml
import time
from munch import munchify
import helpers

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()
with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

nginx_reload_needed = False
if helpers.init_openssl_root_conf():
  nginx_reload_needed = True
if helpers.init_letsencrypt_conf():
  nginx_reload_needed = True

#parse projects
for projectname,project in projects.items():
  os.system(f'/webcrate/scripts/project-dbs.py {projectname}')
  if os.popen(f'/webcrate/scripts/project-certs.py {projectname}').read().strip() == 'True':
    nginx_reload_needed = True

#parse services
for servicename,service in services.items():
  service.name = servicename

  if service.mysql_db:
    mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and helpers.is_mysql_up('webcrate-mysql', mysql_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql_database_found = int(os.popen(f'mysql -u root -h webcrate-mysql -p"{mysql_root_password}" -e "show databases like \'{service.name}\';" | grep "Database ({service.name})" | wc -l').read().strip())
      if mysql_database_found == 0:
        if os.path.isfile(f'/webcrate/secrets/{service.name}-service-mysql.txt'):
          with open(f'/webcrate/secrets/{service.name}-service-mysql.txt', 'r') as f:
            for line in f:
              pair = line.strip().split('=', 1)
              if pair[0] == 'password':
                mysql_service_password = pair[1]
            f.close()
        else:
          mysql_service_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
          with open(f'/webcrate/secrets/{service.name}-service-mysql.txt', 'w') as f:
            f.write(f'host=webcrate-mysql\n')
            f.write(f'name={service.name}\n')
            f.write(f'user={service.name}\n')
            f.write(f'password={mysql_service_password}\n')
            f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-mysql.txt')
        os.system(f'mysql -u root -h webcrate-mysql -p"{mysql_root_password}" -e "CREATE DATABASE \`{service.name}\`;"')
        os.system(f"mysql -u root -h webcrate-mysql -p\"{mysql_root_password}\" -e \"CREATE USER \`{service.name}\`@'%' IDENTIFIED BY \\\"{mysql_service_password}\\\";\"")
        os.system(f"mysql -u root -h webcrate-mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{service.name}\` . * TO \`{service.name}\`@'%';\"")
        os.system(f"mysql -u root -h webcrate-mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql user {service.name} and db created')
      else:
        print(f'mysql user {service.name} and db already exists')

  if service.mysql5_db:
    mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and helpers.is_mysql_up('webcrate-mysql5', mysql5_root_password) == 0:
      retries -= 1
      time.sleep(5)
    if retries > 0:
      mysql5_database_found = int(os.popen(f'mysql -u root -h webcrate-mysql5 -p"{mysql5_root_password}" -e "show databases like \'{service.name}\';" | grep "Database ({service.name})" | wc -l').read().strip())
      if mysql5_database_found == 0:
        if os.path.isfile(f'/webcrate/secrets/{service.name}-service-mysql5.txt'):
          with open(f'/webcrate/secrets/{service.name}-service-mysql5.txt', 'r') as f:
            for line in f:
              pair = line.strip().split('=', 1)
              if pair[0] == 'password':
                mysql5_service_password = pair[1]
            f.close()
        else:
          mysql5_service_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
          with open(f'/webcrate/secrets/{service.name}-service-mysql5.txt', 'w') as f:
            f.write(f'host=webcrate-mysql5\n')
            f.write(f'name={service.name}\n')
            f.write(f'user={service.name}\n')
            f.write(f'password={mysql_service_password}\n')
            f.close()
        with open(f'/webcrate/secrets/{service.name}-service-mysql5.txt', 'w') as f:
          f.write(f'host=webcrate-mysql5\n')
          f.write(f'db={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={mysql5_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-mysql5.txt')
        os.system(f'mysql -u root -h webcrate-mysql5 -p"{mysql5_root_password}" -e "CREATE DATABASE \`{service.name}\`;"')
        os.system(f"mysql -u root -h webcrate-mysql5 -p\"{mysql5_root_password}\" -e \"CREATE USER \`{service.name}\`@'%' IDENTIFIED BY \\\"{mysql5_service_password}\\\";\"")
        os.system(f"mysql -u root -h webcrate-mysql5 -p\"{mysql5_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{service.name}\` . * TO \`{service.name}\`@'%';\"")
        os.system(f"mysql -u root -h webcrate-mysql5 -p\"{mysql5_root_password}\" -e \"FLUSH PRIVILEGES;\"")
        print(f'mysql5 user {service.name} and db created')
      else:
        print(f'mysql5 user {service.name} and db already exists')

  if service.postgresql_db:
    postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
    retries = 20
    while retries > 0 and helpers.is_postgresql_up('webcrate-postgres', postgres_root_password) != '1':
      retries -= 1
      time.sleep(5)
    if retries > 0:
      postgres_database_found = os.popen(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'{service.name}\';"').read().strip()
      if postgres_database_found != '1':
        if os.path.isfile(f'/webcrate/secrets/{service.name}-service-postgres.txt'):
          with open(f'/webcrate/secrets/{service.name}-service-postgres.txt', 'r') as f:
            for line in f:
              pair = line.split('=', 1)
              if pair[0] == 'password':
                postgres_service_password = pair[1]
            f.close()
        else:
          postgres_service_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
          with open(f'/webcrate/secrets/{service.name}-service-postgres.txt', 'w') as f:
            f.write(f'host=webcrate-postgres\n')
            f.write(f'name={service.name}\n')
            f.write(f'user={service.name}\n')
            f.write(f'password={postgres_service_password}\n')
            f.close()
        with open(f'/webcrate/secrets/{service.name}-service-postgres.txt', 'w') as f:
          f.write(f'host=webcrate-postgres\n')
          f.write(f'db={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={postgres_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-postgres.txt')
        os.system(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {service.name} ENCODING \'UTF8\' TEMPLATE template0 LC_COLLATE=\'C\' LC_CTYPE=\'C\';"')
        os.system(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "CREATE USER {service.name} WITH ENCRYPTED PASSWORD \'{postgres_service_password}\';"')
        os.system(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {service.name} TO {service.name};"')
        print(f'postgresql user {service.name} and db created')
      else:
        print(f'postgresql user {service.name} and db already exists')

  if service.https == 'letsencrypt':
    domain = service.domain if service.domain.split('.')[-1] != 'test' else ''
    domain_prev = helpers.load_domains(service.name)
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
    conf = helpers.genereate_openssl_conf(service.name, [service.domain], countryName, organizationName, OPENSSL_EMAIL)
    conf_old = helpers.load_openssl_conf(service.name)
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
    if not os.path.exists(f'/webcrate/nginx/ssl/{service.name}.conf'):
      if (os.path.exists(f'/webcrate/openssl/{service.name}/privkey.pem') and os.path.exists(f'/webcrate/openssl/{service.name}/fullchain.pem')) or (os.path.isdir(f'/webcrate/letsencrypt/live/{service.name}') and os.listdir(f'/webcrate/letsencrypt/live/{service.name}')):
        nginx_reload_needed = True
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', service.https)
        conf = conf.replace('%path%', f'{"live/" if service.https == "letsencrypt" else ""}{service.name}')
        with open(f'/webcrate/nginx/ssl/{service.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        print(f'ssl config for {service.name} - generated')

  if service.https == 'disabled' and os.path.exists(f'/webcrate/nginx/ssl/{service.name}.conf'):
    nginx_reload_needed = True
    os.system(f'rm /webcrate/nginx/ssl/{service.name}.conf')
    print(f'ssl config for {service.name} - removed')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/openssl')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets')

#reload nginx config if needed
if nginx_reload_needed:
  print(f'changes detected - reloading nginx config')
  os.system(f'docker exec webcrate-nginx nginx -s reload')
