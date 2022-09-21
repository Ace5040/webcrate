#!/usr/bin/env python3

import os
import sys
import yaml
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
WEBCRATE_PWD = os.environ.get('WEBCRATE_PWD', '')
UID_START_NUMBER = 100000
SSH_PORT_START_NUMBER = 10000
PROJECT_NAME = sys.argv[1]
volumes = WEBCRATE_PROJECTS_FOLDERS.split(':')

for projectname,project in projects.items():
  if PROJECT_NAME == projectname:
    net_num = project.uid - UID_START_NUMBER
    net_num = f'{net_num // 256}.{net_num % 256}'
    if os.popen(f"docker network inspect webcrate_network_{projectname} >/dev/null 2> /dev/null").read().strip():
      log.write(f'Network webcrate_network_{projectname} exists')
    else:
      log.write(f'Create docker network for {projectname}')
      os.system(f'docker network create --driver=bridge --subnet=10.{net_num}.0/24 webcrate_network_{projectname} > /dev/null')
    project_name = projectname
    backend = f'{project.backend}' + ( '' if ( project.backend_version == 'latest' or ( project.backend == 'php' and project.backend_version == '80') ) else f'{project.backend_version}' )
    container_name = f'webcrate-core-{projectname}'
    ssh_port = SSH_PORT_START_NUMBER + project.uid - UID_START_NUMBER
    project_domain = project.domains[0]
    project_password = project.password
    memcached = project.memcached
    solr = project.solr

    PROJECT_VOLUME=""
    PROJECT_SOLR=""
    volume_path = volumes[project.volume]
    SITES_ABSOLUTE_PATH = volume_path if volume_path[0] == '/' else f'{WEBCRATE_PWD}/{volume_path}'

    if hasattr(project, 'volume'):
      project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{projectname}'
    else:
      project.folder = f'/projects/{projectname}'

    if not os.path.isdir(f'{project.folder}'):
      os.system(f'mkdir -p {project.folder}')
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}')

    PROJECT_VOLUME = f'-v {SITES_ABSOLUTE_PATH}/{projectname}:/home/{projectname}'
    if project.solr:
      SOLR_LOGS = f'{SITES_ABSOLUTE_PATH}/{projectname}/var/solr/logs'
      SOLR_CORES = f'{SITES_ABSOLUTE_PATH}/{projectname}/var/solr/cores'
      os.system(f'mkdir -p {project.folder}/var/solr/logs')
      os.system(f'mkdir -p {project.folder}/var/solr/cores')
      PROJECT_SOLR = f'-v {SOLR_LOGS}:/opt/solr/server/logs -v {SOLR_CORES}:/opt/solr/server/solr/mycores'

    PHP_CONFIGS=""
    if backend in ['php56', 'php73', 'php74', 'php']:
      PHP_CONFIGS = f'-v {WEBCRATE_PWD}/config/php/{backend}.ini:/etc/{backend}/conf.d/user.ini:ro -v {WEBCRATE_PWD}/var/php_pools/{backend}:/webcrate/pools'

    if os.popen(f'docker container inspect {container_name} >/dev/null 2> /dev/null').read().strip():
      log.write(f'Core {container_name} exists')
    else:
      log.write(f'Starting {container_name} container for {projectname}')
      if not os.path.isfile(f'/webcrate/crontabs/{projectname}'):
        os.system(f'echo "" > /webcrate/crontabs/{projectname}')
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/crontabs/{projectname}')
      os.system(f'docker run -d --env-file=/webcrate-readonly/.env --name {container_name} '
        f'--network="webcrate_network_{projectname}" --dns=10.{net_num}.250 '
        f'--restart="unless-stopped" '
        f'-p "{ssh_port}:22" '
        f'-e WEBCRATE_UID={WEBCRATE_UID} '
        f'-e WEBCRATE_GID={WEBCRATE_GID} '
        f'-e WEBCRATE_PROJECT={projectname} '
        f'-e WEBCRATE_PROJECT_PASSWORD={project_password} '
        f'-e WEBCRATE_DOMAIN={project_domain} '
        f'-v /etc/localtime:/etc/localtime:ro '
        f'{PROJECT_VOLUME} '
        f'-v {WEBCRATE_PWD}/var/crontabs/{projectname}:/var/spool/cron/{projectname} '
        f'-v {WEBCRATE_PWD}/config/telegraf:/etc/telegraf/telegraf.d:ro '
        f'-v {WEBCRATE_PWD}/projects.yml:/webcrate/projects.yml:ro '
        f'-v {WEBCRATE_PWD}/var/ssh:/webcrate/ssh_keys '
        f'-v {WEBCRATE_PWD}/var/meta:/webcrate/meta '
        f'-v {WEBCRATE_PWD}/var/log:/webcrate/log '
        f'-v {WEBCRATE_PWD}/config/exim/exim.conf.template:/etc/mail/exim.conf.template '
        f'{PHP_CONFIGS} '
        f'ace5040/webcrate-core-{backend}:stable > /dev/null')

    if project.memcached:
      if os.popen(f'docker container inspect webcrate-{projectname}-memcached >/dev/null 2> /dev/null').read().strip():
        log.write(f'Container webcrate-{projectname}-memcached exists')
      else:
        log.write(f'Starting webcrate-{projectname}-memcached container')
        os.system(f'docker run -d --env-file=/webcrate-readonly/.env --log-driver=none --name webcrate-{projectname}-memcached '
          f'--network="webcrate_network_{projectname}" '
          f'--restart="unless-stopped" '
          f'memcached:1 > /dev/null')

    if project.solr:
      if os.popen(f'docker container inspect webcrate-{projectname}-solr >/dev/null 2> /dev/null').read().strip():
        log.write(f'Container webcrate-{projectname}-solr exists')
      else:
        log.write(f'Starting webcrate-{projectname}-solr container')
        os.system(f'docker run -d --env-file=/webcrate-readonly/.env --log-driver=none --name webcrate-{projectname}-solr '
          f'--network="webcrate_network_{projectname}" '
          f'--restart="unless-stopped" '
          f'--user "{WEBCRATE_UID}:{WEBCRATE_GID}" '
          f'-v /etc/localtime:/etc/localtime:ro '
          f'{PROJECT_SOLR} '
          f'--entrypoint docker-entrypoint.sh '
          f'solr:6 solr -m 4096m -force -f > /dev/null')

    os.system(f'docker network connect --ip=10.{net_num}.250 webcrate_network_{projectname} webcrate-dnsmasq')
    os.system(f'docker network connect webcrate_network_{projectname} webcrate-mysql5')
    os.system(f'docker network connect webcrate_network_{projectname} webcrate-mysql')
    os.system(f'docker network connect webcrate_network_{projectname} webcrate-postgres')
    if WEBCRATE_SERVICE_DOCTOHTML:
      os.system(f'docker network connect webcrate_network_{projectname} webcrate-doctohtml')
    if WEBCRATE_SERVICE_HTMLTOPDF:
      os.system(f'docker network connect webcrate_network_{projectname} webcrate-htmltopdf')
    if WEBCRATE_SERVICE_STATS:
      os.system(f'docker network connect webcrate_network_{projectname} webcrate-influxdb')
    os.system(f'docker network connect webcrate_network_{projectname} webcrate-nginx')

sys.stdout.flush()
