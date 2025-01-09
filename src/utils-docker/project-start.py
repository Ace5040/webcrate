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

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
WEBCRATE_PROJECTS_FOLDERS = os.environ.get('WEBCRATE_PROJECTS_FOLDERS', '')
WEBCRATE_SERVICE_HTMLTOPDF = os.environ.get('WEBCRATE_SERVICE_HTMLTOPDF', 'false') == 'true'
WEBCRATE_SERVICE_DOCTOHTML = os.environ.get('WEBCRATE_SERVICE_DOCTOHTML', 'false') == 'true'
WEBCRATE_SERVICE_STATS = os.environ.get('WEBCRATE_SERVICE_STATS', 'false') == 'true'
WEBCRATE_LOCALDNS = os.environ.get('WEBCRATE_LOCALDNS', 'false') == 'true'
WEBCRATE_PWD = os.environ.get('WEBCRATE_PWD', '')
UID_START_NUMBER = 100000
SSH_PORT_START_NUMBER = 10000
PROJECT_NAME = sys.argv[1]
IS_RELOAD = len(sys.argv) > 2 and sys.argv[2] == 'reload'
volumes = WEBCRATE_PROJECTS_FOLDERS.split(':')

async def initCertificates (project):
  nginx_reload_needed = False
  if project.https == 'letsencrypt':
    domains = ",".join(list(filter(lambda domain: domain.split('.')[-1] != 'test', project.domains)))
    domains_prev = helpers.load_domains(project.name)
    if len(domains) and (domains != domains_prev or not os.path.isdir(f'/webcrate/letsencrypt/live/{project.name}') or not os.listdir(f'/webcrate/letsencrypt/live/{project.name}')):
      retries = 30
      while retries > 0 and not helpers.is_nginx_up():
        retries -= 1
        await asyncio.sleep(2)
      if retries > 0:
        with open(f'/webcrate/letsencrypt-meta/domains-{project.name}.txt', 'w') as f:
          f.write(domains)
          f.close()
        path = f'/webcrate/letsencrypt-meta/well-known/{project.name}'
        if not os.path.isdir(path):
          os.system(f'mkdir -p {path}')
        os.system(f'certbot certonly --key-type ecdsa --keep-until-expiring --renew-with-new-domains --allow-subset-of-names --config-dir /webcrate/letsencrypt --cert-name {project.name} --expand --webroot --webroot-path {path} -d {domains}')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
        os.system(f'rm -rf {path}')
        print(f'{project.name} - letsencrypt certificate generated')
        nginx_reload_needed = True

  if project.https == 'openssl':
    conf = helpers.genereate_openssl_conf(project.name, project.domains)
    conf_old = helpers.load_openssl_conf(project.name)
    if conf_old != conf or not os.path.exists(f'/webcrate/openssl/{project.name}/privkey.pem') or not os.path.exists(f'/webcrate/openssl/{project.name}/fullchain.pem'):
      os.system(f'mkdir -p /webcrate/openssl/{project.name}')
      if os.listdir(f'/webcrate/openssl/{project.name}'):
        os.system(f'rm /webcrate/openssl/{project.name}/*')
      with open(f'/webcrate/openssl/{project.name}/openssl.cnf', 'w') as f:
        f.write(conf)
        f.close()
      os.system(f'openssl genrsa -out /webcrate/openssl/{project.name}/privkey.pem 2048')
      os.system(f'openssl req -new -sha256 -key /webcrate/openssl/{project.name}/privkey.pem -out /webcrate/openssl/{project.name}/fullchain.csr -config /webcrate/openssl/{project.name}/openssl.cnf')
      os.system(f'openssl x509 -req -extensions SAN -extfile /webcrate/openssl/{project.name}/openssl.cnf -in /webcrate/openssl/{project.name}/fullchain.csr -CA /webcrate/secrets/rootCA.crt -CAkey /webcrate/secrets/rootCA.key -CAcreateserial -out /webcrate/openssl/{project.name}/fullchain.pem -days 5000 -sha256')
      os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/openssl/{project.name}')
      nginx_reload_needed = True
      print(f'{project.name} - openssl certificate generated')

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
        print(f'{project.name} - ssl.conf generated')
        nginx_reload_needed = True

  if project.https == 'disabled' and os.path.exists(f'/webcrate/nginx/ssl/{project.name}.conf'):
    nginx_reload_needed = True
    os.system(f'rm /webcrate/nginx/ssl/{project.name}.conf')
    print(f'{project.name} - ssl.conf removed')
  return nginx_reload_needed

async def startMysql (project):
  mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\\$")
  PASS_ENV = ''
  if not os.path.isdir(f'/webcrate/mysql-projects/{project.name}') or not os.listdir(f'/webcrate/mysql-projects/{project.name}'):
    os.system(f'mkdir -p /webcrate/mysql-projects/{project.name}')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/mysql-projects/{project.name}')
    PASS_ENV = f'-e MYSQL_ROOT_PASSWORD="{mysql_root_password}"'
  if helpers.is_container_exists(f'webcrate-{project.name}-mysql'):
    log.write(f'{project.name} - mysql exists')
  else:
    log.write(f'{project.name} - starting mysql container')
    os.system(f'docker run -d --name webcrate-{project.name}-mysql '
      f'--network="webcrate_network_{project.name}" '
      f'--restart="unless-stopped" '
      f'{PASS_ENV} '
      f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
      f'-v /etc/localtime:/etc/localtime:ro '
      f'-v {WEBCRATE_PWD}/var/mysql-projects/{project.name}:/var/lib/mysql '
      f'-v {WEBCRATE_PWD}/config/mysql/mysql.cnf:/etc/mysql/conf.d/user.cnf '
      f'$IMAGE_MARIADB10 >/dev/null')

  retries = 30
  while retries > 0 and helpers.is_mysql_up(f'webcrate-{project.name}-mysql', mysql_root_password) == 0:
    retries -= 1
    await asyncio.sleep(2)
  if retries > 0:
    mysql_database_found = int(os.popen(f'mysql -u root -h webcrate-{project.name}-mysql -p"{mysql_root_password}" -e "show databases like \'{project.name}\';" | grep "Database ({project.name})" | wc -l').read().strip())
    if mysql_database_found == 0:
      if os.path.isfile(f'/webcrate/secrets/{project.name}-project-mysql.txt'):
        with open(f'/webcrate/secrets/{project.name}-project-mysql.txt', 'r') as f:
          for line in f:
            pair = line.strip().split('=', 1)
            if pair[0] == 'password':
              mysql_project_password = pair[1]
          f.close()
      else:
        mysql_project_password=os.popen(f"/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{project.name}-project-mysql.txt', 'w') as f:
          f.write(f'host=webcrate-{project.name}-mysql\n')
          f.write(f'name={project.name}\n')
          f.write(f'user={project.name}\n')
          f.write(f'password={mysql_project_password}\n')
          f.close()
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{project.name}-project-mysql.txt')
        os.system(f'cp /webcrate/secrets/{project.name}-project-mysql.txt {project.folder}/mysql.txt')
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/mysql.txt')
        os.system(f'chmod a-rwx,u+rw {project.folder}/mysql.txt')

      os.system(f'mysql -u root -h webcrate-{project.name}-mysql -p"{mysql_root_password}" -e "CREATE DATABASE \`{project.name}\`;"')
      os.system(f"mysql -u root -h webcrate-{project.name}-mysql -p\"{mysql_root_password}\" -e \"CREATE USER \`{project.name}\`@'%' IDENTIFIED BY \\\"{mysql_project_password}\\\";\"")
      os.system(f"mysql -u root -h webcrate-{project.name}-mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{project.name}\` . * TO \`{project.name}\`@'%';\"")
      os.system(f"mysql -u root -h webcrate-{project.name}-mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
      log.write(f'{project.name} - mysql user and db created')
    else:
      log.write(f'{project.name} - mysql user and db exists')

async def startMysql5 (project):
  mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\\$")
  PASS_ENV = ''
  if not os.path.isdir(f'/webcrate/mysql5-projects/{project.name}') or not os.listdir(f'/webcrate/mysql5-projects/{project.name}'):
    os.system(f'mkdir -p /webcrate/mysql5-projects/{project.name}')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/mysql5-projects/{project.name}')
    PASS_ENV = f'-e MYSQL_ROOT_PASSWORD="{mysql5_root_password}"'
  if helpers.is_container_exists(f'webcrate-{project.name}-mysql5'):
    log.write(f'{project.name} - mysql5 exists')
  else:
    log.write(f'{project.name} - starting mysql5 container')
    os.system(f'docker run -d --name webcrate-{project.name}-mysql5 '
      f'--network="webcrate_network_{project.name}" '
      f'--restart="unless-stopped" '
      f'{PASS_ENV} '
      f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
      f'-v /etc/localtime:/etc/localtime:ro '
      f'-v {WEBCRATE_PWD}/var/mysql5-projects/{project.name}:/var/lib/mysql '
      f'-v {WEBCRATE_PWD}/config/mysql/mysql5.cnf:/etc/mysql/conf.d/user.cnf '
      f'$IMAGE_MARIADB5 >/dev/null')

  retries = 30
  while retries > 0 and helpers.is_mysql_up(f'webcrate-{project.name}-mysql5', mysql5_root_password) == 0:
    retries -= 1
    await asyncio.sleep(2)
  if retries > 0:
    mysql5_database_found = int(os.popen(f'mysql -u root -h webcrate-{project.name}-mysql5 -p"{mysql5_root_password}" -e "show databases like \'{project.name}\';" | grep "Database ({project.name})" | wc -l').read().strip())
    if mysql5_database_found == 0:
      if os.path.isfile(f'/webcrate/secrets/{project.name}-project-mysql5.txt'):
        with open(f'/webcrate/secrets/{project.name}-project-mysql5.txt', 'r') as f:
          for line in f:
            pair = line.strip().split('=', 1)
            if pair[0] == 'password':
              mysql5_project_password = pair[1]
          f.close()
      else:
        mysql5_project_password=os.popen(f"/pwgen.sh").read().strip()
        with open(f'/webcrate/secrets/{project.name}-project-mysql5.txt', 'w') as f:
          f.write(f'host=webcrate-{project.name}-mysql5\n')
          f.write(f'name={project.name}\n')
          f.write(f'user={project.name}\n')
          f.write(f'password={mysql5_project_password}\n')
          f.close()
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{project.name}-project-mysql5.txt')
      os.system(f'cp /webcrate/secrets/{project.name}-project-mysql5.txt {project.folder}/mysql5.txt')
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/mysql5.txt')
      os.system(f'chmod a-rwx,u+rw {project.folder}/mysql5.txt')

      os.system(f'mysql -u root -h webcrate-{project.name}-mysql5 -p"{mysql5_root_password}" -e "CREATE DATABASE \`{project.name}\`;"')
      os.system(f"mysql -u root -h webcrate-{project.name}-mysql5 -p\"{mysql5_root_password}\" -e \"CREATE USER \`{project.name}\`@'%' IDENTIFIED BY \\\"{mysql5_project_password}\\\";\"")
      os.system(f"mysql -u root -h webcrate-{project.name}-mysql5 -p\"{mysql5_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{project.name}\` . * TO \`{project.name}\`@'%';\"")
      os.system(f"mysql -u root -h webcrate-{project.name}-mysql5 -p\"{mysql5_root_password}\" -e \"FLUSH PRIVILEGES;\"")
      log.write(f'{project.name} - mysql5 user and db created')
    else:
      log.write(f'{project.name} - mysql5 user and db exists')

async def startPostgresql (project):
  postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\\$")
  PASS_ENV = ''
  if not os.path.isdir(f'/webcrate/postgresql-projects/{project.name}') or not os.listdir(f'/webcrate/postgresql-projects/{project.name}'):
    os.system(f'mkdir -p /webcrate/postgresql-projects/{project.name}')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/postgresql-projects/{project.name}')
    PASS_ENV = f'-e POSTGRES_PASSWORD="{postgres_root_password}" '
  if helpers.is_container_exists(f'webcrate-{project.name}-postgresql'):
    log.write(f'{project.name} - postgresql exists')
  else:
    log.write(f'{project.name} - starting postgresql container')
    os.system(f'docker run -d --name webcrate-{project.name}-postgresql '
      f'--network="webcrate_network_{project.name}" '
      f'--restart="unless-stopped" '
      f'{PASS_ENV} '
      f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
      f'-v /etc/localtime:/etc/localtime:ro '
      f'-v {WEBCRATE_PWD}/var/postgresql-projects/{project.name}:/var/lib/postgresql/data '
      f'$IMAGE_POSTGRES >/dev/null')

  retries = 30
  while retries > 0 and helpers.is_postgresql_up(f'webcrate-{project.name}-postgresql', postgres_root_password) != '1':
    retries -= 1
    await asyncio.sleep(2)
  if retries > 0:
    postgres_database_found = os.popen(f'psql -d "host=webcrate-{project.name}-postgresql user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'{project.name}\';"').read().strip()
    if postgres_database_found != '1':
      postgres_user_password=os.popen(f"/pwgen.sh").read().strip()
      with open(f'/webcrate/secrets/{project.name}-postgresql.txt', 'w') as f:
        f.write(f'host=webcrate-{project.name}-postgresql\n')
        f.write(f'db={project.name}\n')
        f.write(f'user={project.name}\n')
        f.write(f'password={postgres_user_password}\n')
        f.close()
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{project.name}-postgresql.txt')
      os.system(f'cp /webcrate/secrets/{project.name}-postgresql.txt {project.folder}/postgresql.txt')
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/postgresql.txt')
      os.system(f'chmod a-rwx,u+rw {project.folder}/postgresql.txt')
      os.system(f'psql -d "host=webcrate-{project.name}-postgresql user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {project.name};" >/dev/null')
      os.system(f'psql -d "host=webcrate-{project.name}-postgresql user=postgres password={postgres_root_password}" -tAc "CREATE USER {project.name} WITH ENCRYPTED PASSWORD \'{postgres_user_password}\';" >/dev/null')
      os.system(f'psql -d "host=webcrate-{project.name}-postgresql user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {project.name} TO {project.name};" >/dev/null')
      log.write(f'postgresql user {project.name} and db created')
    else:
      log.write(f'postgresql user {project.name} and db already exists')

async def asyncOps (project):
  initCertificatesTask = asyncio.create_task(initCertificates(project))
  await initCertificatesTask

  #START MYSQL
  if project.mysql_db:
    startMysqlTask = asyncio.create_task(startMysql(project))

  #START MYSQL5
  if project.mysql5_db:
    startMysql5Task = asyncio.create_task(startMysql5(project))

  # START POSTGRESQL
  if project.postgresql_db:
    startPostgresql5Task = asyncio.create_task(startPostgresql(project))

  if project.mysql_db:
    await startMysqlTask
  if project.mysql5_db:
    await startMysql5Task
  if project.postgresql_db:
    await startPostgresql5Task
  return initCertificatesTask.result()

for projectname,project in projects.items():
  if PROJECT_NAME == projectname and project.active:
    project.name = projectname

    # INIT VARIABLES
    backend = f'{project.backend}{"" if project.backend_version == "latest" else project.backend_version }'
    container_name = f'webcrate-core-{project.name}'
    ssh_port = SSH_PORT_START_NUMBER + project.uid - UID_START_NUMBER
    project_domain = project.domains[0]
    project_password = project.password
    memcached = project.memcached
    solr = project.solr

    volume_path = volumes[project.volume]
    SITES_ABSOLUTE_PATH = volume_path if volume_path[0] == '/' else f'{WEBCRATE_PWD}/{volume_path}'


    # CREATE NETWORK
    net_num = project.uid - UID_START_NUMBER
    net_num = f'{net_num // 256}.{net_num % 256}'
    if helpers.is_network_exists(f'webcrate_network_{project.name}'):
      log.write(f'{project.name} - network exists')
    else:
      os.system(f'docker network create --driver=bridge --subnet=10.{net_num}.0/24 webcrate_network_{project.name} >/dev/null')
      log.write(f'{project.name} - network created')

    # INIT PROJECT FOLDER
    project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
    if not os.path.isdir(f'{project.folder}'):
      os.system(f'mkdir -p {project.folder}')
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}')

    # INIT SOLR
    PROJECT_SOLR=''
    if hasattr(project, 'solr') and project.solr:
      if not os.path.isdir(f'{project.folder}/var/solr/logs') or not os.path.isdir(f'{project.folder}/var/solr/cores'):
        os.system(f'mkdir -p {project.folder}/var/solr/logs')
        os.system(f'mkdir -p {project.folder}/var/solr/cores')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/var/solr')
      solr_path = f'{SITES_ABSOLUTE_PATH}/{project.name}/var/solr'
      PROJECT_SOLR = f'-v {solr_path}/logs:/opt/solr/server/logs -v {solr_path}/cores:/opt/solr/server/solr/mycores'

    # INIT ELASTIC
    PROJECT_ELASTIC=''
    if hasattr(project, 'elastic') and project.elastic:
      if not os.path.isdir(f'{project.folder}/var/elastic/data'):
        os.system(f'mkdir -p {project.folder}/var/elastic/data')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/var/elastic')
      PROJECT_ELASTIC = f'-v {SITES_ABSOLUTE_PATH}/{project.name}/var/elastic/data:/usr/share/elasticsearch/data'

    # INIT PHP
    PHP_CONFIGS=''
    if backend in ['php56', 'php73', 'php74', 'php81']:
      PHP_CONFIGS = f'-v {WEBCRATE_PWD}/config/php/{backend}.ini:/etc/{backend}/conf.d/00-user.ini:ro -v {WEBCRATE_PWD}/var/php_pools:/webcrate/pools'

    # START CONTAINER
    if helpers.is_container_exists(f'webcrate-core-{project.name}'):
      log.write(f'{project.name} - core container exists')
    else:
      log.write(f'{project.name} - starting container')
      if not os.path.isfile(f'/webcrate/crontabs/{project.name}'):
        os.system(f'echo "" > /webcrate/crontabs/{project.name}')
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/crontabs/{project.name}')
      os.system(f'docker run -d '
        f'--name {container_name} '
        f'--network="webcrate_network_{project.name}" --dns=10.{net_num}.250 '
        f'--restart="unless-stopped" '
        f'-p "{ssh_port}:22" '
        f'-e WEBCRATE_UID={WEBCRATE_UID} '
        f'-e WEBCRATE_GID={WEBCRATE_GID} '
        f'-e WEBCRATE_PROJECT={project.name} '
        f'-e WEBCRATE_PROJECT_PASSWORD={project_password} '
        f'-e WEBCRATE_DOMAIN={idna.decode(project_domain)} '
        f'-v /etc/localtime:/etc/localtime:ro '
        f'-v {SITES_ABSOLUTE_PATH}/{project.name}:/home/{project.name} '
        f'-v {WEBCRATE_PWD}/var/crontabs/{project.name}:/var/spool/cron/{project.name} '
        f'-v {WEBCRATE_PWD}/projects.yml:/webcrate/projects.yml:ro '
        f'-v {WEBCRATE_PWD}/var/ssh:/webcrate/ssh_keys '
        # f'-v {WEBCRATE_PWD}/var/meta:/webcrate/meta '
        f'-v {WEBCRATE_PWD}/var/log:/webcrate/log '
        f'-v {WEBCRATE_PWD}/config/exim/exim.conf.template:/etc/mail/exim.conf.template '
        f'{PHP_CONFIGS} '
        f'ace5040/webcrate-core-{backend}:latest >/dev/null')
      log.write(f'{project.name} - started container')

    # START MEMCACHED
    if project.memcached:
      if helpers.is_container_exists(f'webcrate-{project.name}-memcached'):
        log.write(f'{project.name} - memcached exists')
      else:
        log.write(f'{project.name} - starting memcached container')
        os.system(f'docker run -d --env-file=/webcrate-readonly/.env --log-driver=none --name webcrate-{project.name}-memcached '
          f'--network="webcrate_network_{project.name}" '
          f'--restart="unless-stopped" '
          f'$IMAGE_MEMCACHED >/dev/null')

    # START SOLR
    if hasattr(project, 'solr') and project.solr:
      if helpers.is_container_exists(f'webcrate-{project.name}-solr'):
        log.write(f'{project.name} - solr exists')
      else:
        log.write(f'{project.name} - starting solr container')
        os.system(f'docker run -d --env-file=/webcrate-readonly/.env --log-driver=none --name webcrate-{project.name}-solr '
          f'--network="webcrate_network_{project.name}" '
          f'--restart="unless-stopped" '
          f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
          f'-v /etc/localtime:/etc/localtime:ro '
          f'{PROJECT_SOLR} '
          f'--entrypoint docker-entrypoint.sh '
          f'$IMAGE_SOLR solr -m 4096m -force -f >/dev/null')

    # START ELASTIC
    if hasattr(project, 'elastic') and project.elastic:
      if helpers.is_container_exists(f'webcrate-{project.name}-elastic'):
        log.write(f'{project.name} - elsatic exists')
      else:
        log.write(f'{project.name} - starting elsatic container')
        # os.system(f'docker run -d --env-file=/webcrate-readonly/.env --log-driver=none --name webcrate-{project.name}-elastic '
        os.system(f'docker run -d --name webcrate-{project.name}-elastic '
          f'--network="webcrate_network_{project.name}" '
          f'--restart="unless-stopped" '
          f'-e "discovery.type=single-node" '
          f'-e "ES_JAVA_OPTS=-Xms8g -Xmx8g" '
          f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
          f'-v /etc/localtime:/etc/localtime:ro '
          f'{PROJECT_ELASTIC} '
          f'--entrypoint docker-entrypoint.sh '
          f'$IMAGE_ELASTICSEARCH > /dev/null')

    #START DATABASES
    if IS_RELOAD:
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-utils-docker')
    else:
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-utils-docker-{project.name}')
    nginx_reload_needed = asyncio.run(asyncOps(project))
    if IS_RELOAD:
      os.system(f'docker network disconnect webcrate_network_{project.name} webcrate-utils-docker')
    else:
      os.system(f'docker network disconnect webcrate_network_{project.name} webcrate-utils-docker-{project.name}')
    # if WEBCRATE_LOCALDNS:
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-dnsmasq'):
      os.system(f'docker network connect --ip=10.{net_num}.250 webcrate_network_{project.name} webcrate-dnsmasq')
    if WEBCRATE_SERVICE_DOCTOHTML:
      if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-doctohtml'):
        os.system(f'docker network connect webcrate_network_{project.name} webcrate-doctohtml')
    if WEBCRATE_SERVICE_HTMLTOPDF:
      if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-htmltopdf'):
        os.system(f'docker network connect webcrate_network_{project.name} webcrate-htmltopdf')
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-nginx'):
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-nginx')
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-phpmyadmin'):
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-phpmyadmin')
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-mysql'):
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-mysql')
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-mysql5'):
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-mysql5')
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-postgres'):
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-postgres')

    if nginx_reload_needed:
      os.system(f'docker exec webcrate-nginx nginx -s reload')
      log.write(f'{project.name} - changes detected - nginx config reloaded')

    log.write(f'{project.name} - started')

sys.stdout.flush()
sys.exit(0)
