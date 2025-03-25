#!/usr/bin/env python3

import os
import yaml
import sys
from munch import munchify
import helpers
from log import log

log = log('/webcrate/log/app.log')
log.write(f'Starting backup process', log.LEVEL.debug)

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
WEBCRATE_FULL_BACKUP_DAYS = os.environ.get('WEBCRATE_FULL_BACKUP_DAYS', '7')
WEBCRATE_MAX_FULL_BACKUPS = os.environ.get('WEBCRATE_MAX_FULL_BACKUPS', '10')
WEBCRATE_BACKUP_URIS = os.environ.get('WEBCRATE_BACKUP_URIS', 'file:///webcrate/backup')
BACKUP_URIS = WEBCRATE_BACKUP_URIS.split('^')
PROJECT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'all'
BACKUP_TYPE = sys.argv[2] if len(sys.argv) > 2 else 'all'

#backup files for webcrate
if PROJECT_NAME == 'admin' or PROJECT_NAME == 'all':
  if ( BACKUP_TYPE == 'files' or BACKUP_TYPE == 'all' ):
    log.write(f'Backup webcrate files', log.LEVEL.debug)
    data_folder = f'/webcrate-readonly'
    log.write(f'=========================================', log.LEVEL.debug)
    log.write(f'backup files webcrate-admin', log.LEVEL.debug)
    log.write(f'=========================================', log.LEVEL.debug)
    sys.stdout.flush()
    for BACKUP_URI in BACKUP_URIS:
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        # f'--asynchronous-upload '
        f'--allow-source-mismatch '
        f'--volsize 5000 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--include {data_folder}/config '
        f'--include {data_folder}/var/crontabs '
        f'--include {data_folder}/var/letsencrypt '
        f'--include {data_folder}/var/letsencrypt-meta '
        f'--include {data_folder}/var/openssl '
        f'--include {data_folder}/var/secrets '
        f'--include {data_folder}/var/ssh '
        f'--include {data_folder}/.env '
        f'--include {data_folder}/projects.yml '
        f'--include {data_folder}/redirects.yml '
        f'--include {data_folder}/services.yml '
        f'--exclude "**" '
        f'"{data_folder}" '
        f'"{BACKUP_URI}/webcrate/files"'
      )
      sys.stdout.flush()
      #remove old backup files for webcrate
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{BACKUP_URI}/webcrate/files"'
      )
      sys.stdout.flush()
  if ( BACKUP_TYPE == 'mysql' or BACKUP_TYPE == 'all' ):
    #backup mysql for webcrate
    log.write(f'Backup webcrate-admin mysql database', log.LEVEL.debug)
    log.write(f'=========================================', log.LEVEL.debug)
    log.write(f'backup mysql db for webcrate-admin', log.LEVEL.debug)
    log.write(f'=========================================', log.LEVEL.debug)
    sys.stdout.flush()
    mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\\$")
    os.system(f'mkdir -p /webcrate/backup-tmp')
    if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
      os.system(f'rm /webcrate/backup-tmp/*')
    os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h webcrate-mysql -u root -p"{mysql_root_password}" --result-file "/webcrate/backup-tmp/webcrate.sql" "webcrate"')
    for BACKUP_URI in BACKUP_URIS:
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
        f'--num-retries 3 '
        # f'--asynchronous-upload '
        f'--volsize 5000 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup-tmp" '
        f'"{BACKUP_URI}/webcrate/mysql"'
      )
      sys.stdout.flush()
      #remove old mysql backup for webcrate
      os.system(f'duplicity --verbosity notice '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'--force '
        f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
        f'"{BACKUP_URI}/webcrate/mysql"'
      )
      sys.stdout.flush()
    if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
      os.system(f'rm /webcrate/backup-tmp/*')

for projectname,project in projects.items():
  project.name = projectname
  if project.backup and project.active and ( PROJECT_NAME == projectname or PROJECT_NAME == 'all' ):

    #backup files
    if ( BACKUP_TYPE == 'files' or BACKUP_TYPE == 'all' ):
      log.write(f'=========================================', log.LEVEL.debug)
      log.write(f'backup files for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      sys.stdout.flush()
      if hasattr(project, 'volume'):
        project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
      else:
        project.folder = f'/projects/{project.name}'
      log.write(f'Backup files for project {project.name}', log.LEVEL.debug)
      data_folder = f'{project.folder}/{project.root_folder.split("/")[0]}'
      FILTERS = ''
      if hasattr(project, 'duplicity_filters'):
        for duplicity_filter in project.duplicity_filters:
          FILTERS = f'{FILTERS}--{duplicity_filter.mode} "{data_folder}/{duplicity_filter.path}" '
      if os.path.isdir(f'{data_folder}'):
        for BACKUP_URI in BACKUP_URIS:
          os.system(f'duplicity --verbosity notice '
            f'--no-encryption '
            f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
            f'--num-retries 3 '
            # f'--asynchronous-upload '
            f'--allow-source-mismatch '
            f'--volsize 5000 '
            f'--archive-dir /webcrate/duplicity/.duplicity '
            f'--log-file /webcrate/duplicity/duplicity.log '
            f'{FILTERS}'
            f'"{data_folder}" '
            f'"{BACKUP_URI}/projects/{project.name}/files"'
          )
          sys.stdout.flush()
          os.system(f'duplicity --verbosity notice '
            f'--archive-dir /webcrate/duplicity/.duplicity '
            f'--log-file /webcrate/duplicity/duplicity.log '
            f'--force '
            f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
            f'"{BACKUP_URI}/projects/{project.name}/files"'
          )
          sys.stdout.flush()
      #backup solr cores
      log.write(f'Backup solr cores for project {project.name}', log.LEVEL.debug)
      if os.path.isdir(f'{project.folder}/var/solr/cores'):
        for BACKUP_URI in BACKUP_URIS:
          os.system(f'duplicity --verbosity notice '
            f'--no-encryption '
            f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
            f'--num-retries 3 '
            # f'--asynchronous-upload '
            f'--allow-source-mismatch '
            f'--volsize 5000 '
            f'--archive-dir /webcrate/duplicity/.duplicity '
            f'--log-file /webcrate/duplicity/duplicity.log '
            f'--exclude "{project.folder}/var/solr/cores/**/data" '
            f'"{project.folder}/var/solr/cores" '
            f'"{BACKUP_URI}/projects/{project.name}/solr-cores"'
          )
          sys.stdout.flush()
          os.system(f'duplicity --verbosity notice '
            f'--archive-dir /webcrate/duplicity/.duplicity '
            f'--log-file /webcrate/duplicity/duplicity.log '
            f'--force '
            f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
            f'"{BACKUP_URI}/projects/{project.name}/solr-cores"'
          )
          sys.stdout.flush()

    #connect to project network
    if not helpers.is_network_has_connection(f'webcrate_network_{project.name}', 'webcrate-utils-docker'):
      os.system(f'docker network connect webcrate_network_{project.name} webcrate-utils-docker')

    #backup mysql
    if project.mysql_db and ( BACKUP_TYPE == 'mysql' or BACKUP_TYPE == 'all' ):
      log.write(f'Backup webcrate-mysql db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      log.write(f'backup mysql db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      sys.stdout.flush()
      mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\\$")
      os.system(f'mkdir -p /webcrate/backup-tmp')
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h webcrate-mysql -u root -p"{mysql_root_password}" --result-file "/webcrate/backup-tmp/{project.name}.sql" "{project.name}"')
      for BACKUP_URI in BACKUP_URIS:
        os.system(f'duplicity --verbosity notice '
          f'--no-encryption '
          f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
          f'--num-retries 3 '
          # f'--asynchronous-upload '
          f'--volsize 5000 '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'"/webcrate/backup-tmp" '
          f'"{BACKUP_URI}/projects/{project.name}/mysql"'
        )
        sys.stdout.flush()
        os.system(f'duplicity --verbosity notice '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'--force '
          f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
          f'"{BACKUP_URI}/projects/{project.name}/mysql"'
        )
        sys.stdout.flush()
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')


    #backup project mysql
    if project.mysql_db and ( BACKUP_TYPE == 'mysql' or BACKUP_TYPE == 'all' ):
      log.write(f'Backup project-mysql db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      log.write(f'backup project mysql db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      sys.stdout.flush()
      mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\\$")
      os.system(f'mkdir -p /webcrate/backup-tmp')
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h webcrate-{project.name}-mysql -u root -p"{mysql_root_password}" --result-file "/webcrate/backup-tmp/{project.name}.sql" "{project.name}"')
      for BACKUP_URI in BACKUP_URIS:
        os.system(f'duplicity --verbosity notice '
          f'--no-encryption '
          f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
          f'--num-retries 3 '
          # f'--asynchronous-upload '
          f'--volsize 5000 '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'"/webcrate/backup-tmp" '
          f'"{BACKUP_URI}/projects/{project.name}/project-mysql"'
        )
        sys.stdout.flush()
        os.system(f'duplicity --verbosity notice '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'--force '
          f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
          f'"{BACKUP_URI}/projects/{project.name}/project-mysql"'
        )
        sys.stdout.flush()
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')

    #backup project mysql5
    if project.mysql5_db and ( BACKUP_TYPE == 'mysql5' or BACKUP_TYPE == 'all' ):
      log.write(f'=========================================', log.LEVEL.debug)
      log.write(f'backup project-mysql5 db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      sys.stdout.flush()
      log.write(f'Backup project-mysql5 db for project {project.name}', log.LEVEL.debug)
      mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\\$")
      os.system(f'mkdir -p /webcrate/backup-tmp')
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h webcrate-{project.name}-mysql5 -u root -p"{mysql5_root_password}" --result-file "/webcrate/backup-tmp/{project.name}.sql" "{project.name}"')
      for BACKUP_URI in BACKUP_URIS:
        os.system(f'duplicity --verbosity notice '
          f'--no-encryption '
          f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
          f'--num-retries 3 '
          # f'--asynchronous-upload '
          f'--volsize 5000 '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'"/webcrate/backup-tmp" '
          f'"{BACKUP_URI}/projects/{project.name}/project-mysql5"'
        )
        sys.stdout.flush()
        os.system(f'duplicity --verbosity notice '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'--force '
          f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
          f'"{BACKUP_URI}/projects/{project.name}/project-mysql5"'
        )
        sys.stdout.flush()
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')

    #backup postgresql
    if project.postgresql_db and ( BACKUP_TYPE == 'postgresql' or BACKUP_TYPE == 'all' ):
      log.write(f'=========================================', log.LEVEL.debug)
      log.write(f'backup postgresql db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      sys.stdout.flush()
      log.write(f'Backup postgres db for project {project.name}', log.LEVEL.debug)
      postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\\$")
      os.system(f'mkdir -p /webcrate/backup-tmp')
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')
      os.system(f'PGPASSWORD={postgres_root_password} pg_dump -U postgres -h webcrate-postgres {project.name} > /webcrate/backup-tmp/{project.name}.pgsql')
      for BACKUP_URI in BACKUP_URIS:
        os.system(f'duplicity --verbosity notice '
          f'--no-encryption '
          f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
          f'--num-retries 3 '
          # f'--asynchronous-upload '
          f'--volsize 5000 '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'"/webcrate/backup-tmp" '
          f'"{BACKUP_URI}/projects/{project.name}/postgresql"'
        )
        sys.stdout.flush()
        os.system(f'duplicity --verbosity notice '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'--force '
          f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
          f'"{BACKUP_URI}/projects/{project.name}/postgresql"'
        )
        sys.stdout.flush()
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')

    #backup project postgresql
    if project.postgresql_db and ( BACKUP_TYPE == 'postgresql' or BACKUP_TYPE == 'all' ):
      log.write(f'=========================================', log.LEVEL.debug)
      log.write(f'backup project-postgresql db for project {project.name}', log.LEVEL.debug)
      log.write(f'=========================================', log.LEVEL.debug)
      sys.stdout.flush()
      log.write(f'Backup project-postgresql db for project {project.name}', log.LEVEL.debug)
      postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\\$")
      os.system(f'mkdir -p /webcrate/backup-tmp')
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')
      os.system(f'PGPASSWORD={postgres_root_password} pg_dump -U postgres -h webcrate-{project.name}-postgresql {project.name} > /webcrate/backup-tmp/{project.name}.pgsql')
      for BACKUP_URI in BACKUP_URIS:
        os.system(f'duplicity --verbosity notice '
          f'--no-encryption '
          f'--full-if-older-than {WEBCRATE_FULL_BACKUP_DAYS}D '
          f'--num-retries 3 '
          # f'--asynchronous-upload '
          f'--volsize 5000 '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'"/webcrate/backup-tmp" '
          f'"{BACKUP_URI}/projects/{project.name}/project-postgresql"'
        )
        sys.stdout.flush()
        os.system(f'duplicity --verbosity notice '
          f'--archive-dir /webcrate/duplicity/.duplicity '
          f'--log-file /webcrate/duplicity/duplicity.log '
          f'--force '
          f'remove-all-but-n-full {WEBCRATE_MAX_FULL_BACKUPS} '
          f'"{BACKUP_URI}/projects/{project.name}/project-postgresql"'
        )
        sys.stdout.flush()
      if os.path.isdir(f'/webcrate/backup-tmp') and os.listdir(f'/webcrate/backup-tmp'):
        os.system(f'rm /webcrate/backup-tmp/*')
    #disconnect from project network
    os.system(f'docker network disconnect webcrate_network_{project.name} webcrate-utils-docker')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/backup')
os.system(f'chmod -R a-rw,u+rw /webcrate/backup')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/duplicity')
log.write(f'Backup process ended', log.LEVEL.debug)
sys.stdout.flush()
