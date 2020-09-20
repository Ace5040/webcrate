#!/usr/bin/env python3

import os
import yaml
import time
from munch import munchify
from pprint import pprint

with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

def is_mysql_up(host, password):
  return int(os.popen(f'mysql -u root -h {host} -p"{password}" -e "show databases;" | grep "Database" | wc -l').read().strip())

def is_postgresql_up(host, password):
  return os.popen(f'psql -d "host={host} user=postgres password={password}" -tAc "SELECT 1 FROM pg_database LIMIT 1;"').read().strip()

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
        mysql_service_password=os.popen(f"docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh").read().strip()
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
        mysql5_service_password=os.popen(f"docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh").read().strip()
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
      postgres_database_found = os.popen(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'postgres\';"').read().strip()
      if postgres_database_found != '1':
        postgres_service_password=os.popen(f"docker run --rm ace5040/webcrate-utils:stable /webcrate/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{service.name}-service-postgres.txt', 'w') as f:
          f.write(f'host=postgres\n')
          f.write(f'db={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={postgres_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-postgres.txt')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {service.name};"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "CREATE USER {service.name} WITH ENCRYPTED PASSWORD \'{postgres_service_password}\';"')
        os.system(f'psql -d "host=postgres user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {service.name} TO {service.name};"')
        print(f'postgresql user {service.name} and db created')
      else:
        print(f'postgresql user {service.name} and db already exists')
