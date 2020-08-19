#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/users.yml') as f:
  users = munchify(yaml.safe_load(f))

SITES_PATH = '/sites'
MODE = os.environ.get('WEBCRATE_MODE', 'DEV')

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
        f'"file:///webcrate/backup/users/{user.name}/files" '
      )
    #backup mysql
    if user.mysql_db:
      print(f'backup mysql db for user {user.name}')
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql -u root -pmysql --result-file "/webcrate/backup/tmp/{user.name}.sql" "{user.name}"')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"file:///webcrate/backup/users/{user.name}/mysql" '
      )
      os.system(f'rm /webcrate/backup/tmp/*')
    #backup mysql5
    if user.mysql5_db:
      print(f'backup mysql5 db for user {user.name}')
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')
      os.system(f'mysqldump --single-transaction --max_allowed_packet=64M -h mysql5 -u root -pmysql --result-file "/webcrate/backup/tmp/{user.name}.sql" "{user.name}"')
      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"file:///webcrate/backup/users/{user.name}/mysql5" '
      )
      os.system(f'rm /webcrate/backup/tmp/*')
    #backup postgresql
    if user.postgresql_db:
      print(f'backup postgresql db for user {user.name}')
      os.system(f'mkdir -p /webcrate/backup/tmp')
      os.system(f'rm /webcrate/backup/tmp/*')

      os.system(f'PGPASSWORD={PGPASS} pg_dump -U postgres -h postgres {user.name} > /webcrate/backup/tmp/{user.name}.pgsql')

      os.system(f'duplicity --verbosity notice '
        f'--no-encryption '
        f'--full-if-older-than 14D '
        f'--num-retries 3 '
        f'--asynchronous-upload '
        f'--volsize 100 '
        f'--archive-dir /webcrate/duplicity/.duplicity '
        f'--log-file /webcrate/duplicity/duplicity.log '
        f'"/webcrate/backup/tmp" '
        f'"file:///webcrate/backup/users/{user.name}/postgresql" '
      )
      os.system(f'rm /webcrate/backup/tmp/*')
