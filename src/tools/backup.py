#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint
from log import log

log = log('/webcrate/meta/webcrate.log')
log.write(f'Starting backup process')

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
WEBCRATE_FULL_BACKUP_DAYS = os.environ.get('WEBCRATE_FULL_BACKUP_DAYS', '7')
WEBCRATE_MAX_FULL_BACKUPS = os.environ.get('WEBCRATE_MAX_FULL_BACKUPS', '10')
REMOTE_BACKUP_URI = os.environ.get('REMOTE_BACKUP_URI', 'file:///webcrate/backup')

#backup webcrate
log.write(f'Backup webcrate files')
data_folder = f'/webcrate-readonly'
print(f'backup files webcrate-admin')
os.system(f'duplicity --verbosity notice '
  f'--no-encryption '
  f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
  f'--num-retries 3 '
  f'--asynchronous-upload '
  f'--allow-source-mismatch '
  f'--volsize 500 '
  f'--archive-dir /webcrate/duplicity/.duplicity '
  f'--log-file /webcrate/duplicity/duplicity.log '
  f'--include {data_folder}/config '
  f'--include {data_folder}/var/crontabs '
  f'--include {data_folder}/var/letsencrypt '
  f'--include {data_folder}/var/openssl '
  f'--include {data_folder}/var/secrets '
  f'--include {data_folder}/var/ssh '
  f'--include {data_folder}/var/synapse '
  f'--include {data_folder}/.env '
  f'--include {data_folder}/projects.yml '
  f'--include {data_folder}/services.yml '
  f'--exclude "**" '
  f'"{data_folder}" '
  f'"{REMOTE_BACKUP_URI}/webcrate/files"'
)
os.system(f'duplicity --verbosity notice '
  f'--archive-dir /webcrate/duplicity/.duplicity '
  f'--log-file /webcrate/duplicity/duplicity.log '
  f'--force '
  f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
  f'"{REMOTE_BACKUP_URI}/webcrate/files"'
)

#backup webcrate mysql
log.write(f'Backup webcrate-admin mysql database')
print(f'backup mysql db for webcrate-admin')
mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
os.system(f'mkdir -p /webcrate/backup/tmp')
os.system(f'rm /webcrate/backup/tmp/*')
os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql -u root -p"{mysql_root_password}" --result-file "/webcrate/backup/tmp/webcrate.sql" "webcrate"')
os.system(f'duplicity --verbosity notice '
  f'--no-encryption '
  f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
  f'--num-retries 3 '
  f'--asynchronous-upload '
  f'--volsize 500 '
  f'--archive-dir /webcrate/duplicity/.duplicity '
  f'--log-file /webcrate/duplicity/duplicity.log '
  f'"/webcrate/backup/tmp" '
  f'"{REMOTE_BACKUP_URI}/webcrate/mysql"'
)
os.system(f'rm /webcrate/backup/tmp/*')
os.system(f'duplicity --verbosity notice '
  f'--archive-dir /webcrate/duplicity/.duplicity '
  f'--log-file /webcrate/duplicity/duplicity.log '
  f'--force '
  f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
  f'"{REMOTE_BACKUP_URI}/webcrate/mysql"'
)

for projectname,project in projects.items():
  project.name = projectname
  if project.backup:
    if hasattr(project, 'volume'):
      project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
    else:
      project.folder = f'/projects/{project.name}'
    #backup files
    log.write(f'Backup files for project {project.name}')
    data_folder = f'{project.folder}/{project.root_folder.split("/")[0]}'
    FILTERS = ''
    if hasattr(project, 'duplicity_filters'):
      for duplicity_filter in project.duplicity_filters:
        FILTERS = f'{FILTERS}--{duplicity_filter.mode} "{data_folder}/{duplicity_filter.path}" '
    if os.path.isdir(f'{data_folder}'):
      print(f'backup files for project {project.name}')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--allow-source-mismatch '
        f'--volsize 500 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'{FILTERS}'
        f'"{data_folder}" '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/files"'
      )
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/files"'
      )
    #backup solr cores
    log.write(f'Backup solr cores for project {project.name}')
    if os.path.isdir(f'{project.folder}/var/solr/cores'):
      print(f'backup files for project {project.name}')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--allow-source-mismatch '
        f'--volsize 500 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--exclude "{project.folder}/var/solr/cores/**/data" '
        f'--include {project.folder}/var/solr/cores '
        f'"{project.folder}/var/solr/cores" '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/solr-cores"'
      )
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/solr-cores"'
      )
    #backup mysql
    if project.mysql_db:
      log.write(f'Backup mysql db for project {project.name}')
      print(f'backup mysql db for project {project.name}')
      mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql -u root -p"{mysql_root_password}" --result-file "/webcrate/backup/tmp/{project.name}.sql" "{project.name}"')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 500 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/mysql"'
      )
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/mysql"'
      )
    #backup mysql5
    if project.mysql5_db:
      print(f'backup mysql5 db for project {project.name}')
      log.write(f'Backup mysql5 db for project {project.name}')
      mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql5 -u root -p"{mysql5_root_password}" --result-file "/webcrate/backup/tmp/{project.name}.sql" "{project.name}"')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 500 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/mysql5"'
      )
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/mysql5"'
      )
    #backup postgresql
    if project.postgresql_db:
      print(f'backup postgresql db for project {project.name}')
      log.write(f'Backup postgres db for project {project.name}')
      postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'PGPASSWORD={postgres_root_password} pg_dump -U postgres -h postgres {project.name} > /webcrate/backup/tmp/{project.name}.pgsql')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 500 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/postgresql"'
      )
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{REMOTE_BACKUP_URI}/projects/{project.name}/postgresql"'
      )

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/backup')
os.system(f'chmod -R a-rw,u+rw /webcrate/backup')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/duplicity')
log.write(f'Backup process ended')
