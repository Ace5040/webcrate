#!/usr/bin/env python3

import os
import sys
import yaml
import helpers
import asyncio
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
WEBCRATE_SERVICE_HTMLTOPDF = os.environ.get('WEBCRATE_SERVICE_HTMLTOPDF', 'false') == 'true'
WEBCRATE_SERVICE_DOCTOHTML = os.environ.get('WEBCRATE_SERVICE_DOCTOHTML', 'false') == 'true'
WEBCRATE_SERVICE_STATS = os.environ.get('WEBCRATE_SERVICE_STATS', 'false') == 'true'
WEBCRATE_PWD = os.environ.get('WEBCRATE_PWD', '')

helpers.init_openssl_root_conf()
helpers.init_letsencrypt_conf()

async def startMysql (service):
  mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\\$")
  PASS_ENV = ''
  if not os.path.isdir(f'/webcrate/mysql-services/{service.name}') or not os.listdir(f'/webcrate/mysql-services/{service.name}'):
    os.system(f'mkdir -p /webcrate/mysql-services/{service.name}')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/mysql-services/{service.name}')
    PASS_ENV = f'-e MYSQL_ROOT_PASSWORD="{mysql_root_password}"'
  if helpers.is_container_exists(f'webcrate-{service.name}-mysql'):
    log.write(f'{service.name} - mysql exists')
  else:
    log.write(f'{service.name} - starting mysql container')
    os.system(f'docker run -d --name webcrate-{service.name}-mysql '
      f'--network="webcrate_network" '
      f'--restart="unless-stopped" '
      f'{PASS_ENV} '
      f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
      f'-v /etc/localtime:/etc/localtime:ro '
      f'-v {WEBCRATE_PWD}/var/mysql-services/{service.name}:/var/lib/mysql '
      f'-v {WEBCRATE_PWD}/config/mysql/mysql.cnf:/etc/mysql/conf.d/user.cnf '
      f'$IMAGE_MARIADB10 >/dev/null')

  retries = 30
  while retries > 0 and helpers.is_mysql_up(f'webcrate-{service.name}-mysql', mysql_root_password) == 0:
    retries -= 1
    await asyncio.sleep(2)
  if retries > 0:
    mysql_database_found = int(os.popen(f'mysql -u root -h webcrate-{service.name}-mysql -p"{mysql_root_password}" -e "show databases like \'{service.name}\';" | grep "Database ({service.name})" | wc -l').read().strip())
    if mysql_database_found == 0:
      if os.path.isfile(f'/webcrate/secrets/{service.name}-service-mysql.txt'):
        with open(f'/webcrate/secrets/{service.name}-service-mysql.txt', 'r') as f:
          for line in f:
            pair = line.strip().split('=', 1)
            if pair[0] == 'password':
              mysql_service_password = pair[1]
          f.close()
      else:
        mysql_service_password=os.popen(f"/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{service.name}-service-mysql.txt', 'w') as f:
          f.write(f'host=webcrate-{service.name}-mysql\n')
          f.write(f'name={service.name}\n')
          f.write(f'user={service.name}\n')
          f.write(f'password={mysql_service_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{service.name}-service-mysql.txt')

      os.system(f'mysql -u root -h webcrate-{service.name}-mysql -p"{mysql_root_password}" -e "CREATE DATABASE \`{service.name}\`;"')
      os.system(f"mysql -u root -h webcrate-{service.name}-mysql -p\"{mysql_root_password}\" -e \"CREATE USER \`{service.name}\`@'%' IDENTIFIED BY \\\"{mysql_service_password}\\\";\"")
      os.system(f"mysql -u root -h webcrate-{service.name}-mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{service.name}\` . * TO \`{service.name}\`@'%';\"")
      os.system(f"mysql -u root -h webcrate-{service.name}-mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
      log.write(f'{service.name} - mysql user and db created')
    else:
      log.write(f'{service.name} - mysql user and db exists')

async def startDatabases (service):
    #START MYSQL
    if service.mysql_db:
      startMysqlTask = asyncio.create_task(startMysql(service))
    if service.mysql_db:
      await startMysqlTask

for servicename,service in services.items():
  service.name = servicename

  # INIT VARIABLES
  # container_name = f'webcrate-core-{service.name}'
  # service_domain = service.domains[0]
  # service_password = service.password

  # CREATE NETWORK
  # if helpers.is_network_exists(f'webcrate_network_{service.name}'):
  #   log.write(f'{service.name} - network exists')
  # else:
  #   os.system(f'docker network create --driver=bridge webcrate_network{service.name} >/dev/null')
  #   log.write(f'{service.name} - network created')

  # START DATABASES
  os.system(f'docker network connect webcrate_network webcrate-utils-docker-services-init')
  asyncio.run(startDatabases(service))
  os.system(f'docker network disconnect webcrate_network webcrate-utils-docker-services-init')

  if not helpers.is_network_has_connection(f'webcrate_network', 'webcrate-nginx'):
    os.system(f'docker network connect webcrate_network webcrate-nginx')

dbHosts = 'webcrate-mysql'
for servicename,service in services.items():
  service.name = servicename
  if service.mysql_db:
    dbHosts = f'{dbHosts},webcrate-{service.name}-mysql'

for projectname,project in projects.items():
  project.name = projectname
  if project.mysql_db:
    dbHosts = f'{dbHosts},webcrate-{project.name}-mysql'
  if project.mysql5_db:
    dbHosts = f'{dbHosts},webcrate-{project.name}-mysql5'

with open(f'/webcrate/meta/dbhosts.txt', 'w') as f:
  f.write(dbHosts)
  f.close()

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/meta')

sys.stdout.flush()
