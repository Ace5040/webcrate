#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_PROJECT = os.environ.get('WEBCRATE_PROJECT', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
os.system(f'userdel dev > /dev/null 2>&1')

for projectname,project in projects.items():
  project.name = projectname
  if WEBCRATE_PROJECT == project.name:
    project.folder = f'/home/{project.name}'
    log.write(f'Create user and group for {project.name}')
    os.system(f'groupadd --non-unique --gid {WEBCRATE_GID} {project.name}')
    os.system(f'useradd --non-unique --no-create-home --uid {WEBCRATE_UID} --gid {WEBCRATE_GID} --home-dir {project.folder} {project.name}')
    os.system(f'usermod -s /bin/bash {project.name} > /dev/null 2>&1')
    password = str(project.password).replace("$", "\$")
    os.system(f'usermod -p {password} {project.name} > /dev/null 2>&1')
    if project.backend == 'gunicorn':
      log.write(f'Start gunicorn for {project.name}')
      data_folder=project.root_folder.split("/")[0]
      gunicorn_conf=''
      if os.path.isfile(f'{project.folder}/{data_folder}/gunicorn.conf.py'):
        gunicorn_conf=f'-c {project.folder}/{data_folder}/gunicorn.conf.py'
      if(os.path.isfile(f'{project.folder}/{data_folder}/gunicorn.init')):
        os.system(f'rm {project.folder}/{data_folder}/gunicorn.init')
        os.system(f'sudo -iu {project.name} bash -c "cd {project.folder}/{data_folder}; pip install gunicorn; pip freeze > requirements.txt"')
      os.system(f'sudo -iu {project.name} bash -c "gunicorn --daemon --bind :9000 --name {project.name} --user {project.name} --group {project.name} --pid ../tmp/gunicorn.pid --error-logfile ../log/gunicorn-error.log {gunicorn_conf} --chdir {project.folder}/{data_folder} {project.gunicorn_app_module}"')
    print(f'{project.name} - created')
