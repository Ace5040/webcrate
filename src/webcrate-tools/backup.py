#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()

SITES_PATH = '/sites'
WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
REMOTE_BACKUP_URI = os.environ.get('REMOTE_BACKUP_URI', 'file:///webcrate/backup')

for username,user in users.items():
  user.name = username
  if user.backup:
    #backup files
    data_folder = f'{SITES_PATH}/{user.name}/{user.root_folder.split("/")[0]}'
    if os.path.isdir(f'{data_folder}'):
      print(f'backup files for user {user.name}')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"{data_folder}" '
        f'"{REMOTE_BACKUP_URI}/users/{user.name}/files"'
      )
    #backup mysql
    if user.mysql_db:
      print(f'backup mysql db for user {user.name}')
      mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql -u root -p"{mysql_root_password}" --result-file "/webcrate/backup/tmp/{user.name}.sql" "{user.name}"')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"{REMOTE_BACKUP_URI}/users/{user.name}/mysql"'
      )
      os.system(f'rm /webcrate/backup/tmp/*')
    #backup mysql5
    if user.mysql5_db:
      print(f'backup mysql5 db for user {user.name}')
      mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql5 -u root -p"{mysql5_root_password}" --result-file "/webcrate/backup/tmp/{user.name}.sql" "{user.name}"')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"{REMOTE_BACKUP_URI}/users/{user.name}/mysql5"'
      )
      os.system(f'rm /webcrate/backup/tmp/*')
    #backup postgresql
    if user.postgresql_db:
      print(f'backup postgresql db for user {user.name}')
      postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("=")[1][1:][:-1].replace("$", "\$")
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'PGPASSWORD={postgres_root_password} pg_dump -U postgres -h postgres {user.name} > /webcrate/backup/tmp/{user.name}.pgsql')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"{REMOTE_BACKUP_URI}/users/{user.name}/postgresql"'
      )
      os.system(f'rm /webcrate/backup/tmp/*')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/backup')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/duplicity')
