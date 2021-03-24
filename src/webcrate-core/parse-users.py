#!/usr/bin/env python3

import os
import yaml
from munch import munchify

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
UID_START_NUMBER = 100000
CGI_PORT_START_NUMBER = 9000

if WEBCRATE_MODE == 'PRODUCTION':
  os.system(f'userdel dev > /dev/null 2>&1')

if WEBCRATE_MODE == 'DEV':
  os.system(f'usermod -u {WEBCRATE_UID} dev > /dev/null 2>&1')
  os.system(f'groupmod -g {WEBCRATE_GID} dev > /dev/null 2>&1')
  os.system(f'usermod -s /bin/fish dev > /dev/null 2>&1')

for username,user in users.items():
  user.name = username
  user.folder = f'/projects{(user.volume + 1) if user.volume else ""}/{user.name}'
  UID = user.uid
  GID = user.uid

  if WEBCRATE_MODE == 'DEV':
    UID = WEBCRATE_UID
    GID = WEBCRATE_GID

  os.system(f'groupadd --non-unique --gid {GID} {user.name}')
  os.system(f'useradd --non-unique --no-create-home --uid {UID} --gid {GID} --home-dir {user.folder} {user.name}')
  os.system(f'usermod -s /bin/fish {user.name} > /dev/null 2>&1')
  os.system(f'chown {user.name}:{user.name} {user.folder}')
  password = str(user.password).replace("$", "\$")
  os.system(f'usermod -p {password} {user.name} > /dev/null 2>&1')

  if hasattr(user, 'ftps') and user.ftps:
    with open(f'/etc/ftp.passwd', 'a') as f:
      for ftp in user.ftps:
        ftp_folder = f'{user.folder}{("/" + ftp.home) if ftp.home else ""}'
        f.write(f'{ftp.name}:{ftp.password}:{UID}:{GID}::{ftp_folder}:/bin/false\n')
        os.system(f'mkdir -p {ftp_folder}')
        os.system(f'chown -R {user.name}:{user.name} {ftp_folder}')
      f.close()
    os.system(f'chmod a-rwx,u+rw /etc/ftp.passwd')
    print(f'additional ftp accounts for {user.name} - generated')

  if user.backend == 'gunicorn':
    data_folder=user.root_folder.split("/")[0]
    port = CGI_PORT_START_NUMBER + user.uid - UID_START_NUMBER
    gunicorn_conf=''
    if os.path.isfile(f'{user.folder}/{data_folder}/gunicorn.conf.py'):
      gunicorn_conf=f'-c {user.folder}/{data_folder}/gunicorn.conf.py'
    os.system(f'source {user.folder}/{data_folder}/env/bin/activate; sudo -u {user.name} gunicorn --daemon --bind :{port} --name {user.name} --user {user.name} --group {user.name} --pid ../tmp/gunicorn.pid --error-logfile ../log/gunicorn-error.log {gunicorn_conf} --chdir {user.folder}/{data_folder} {user.gunicorn_app_module}; deactivate')

  print(f'{user.name} - created')
