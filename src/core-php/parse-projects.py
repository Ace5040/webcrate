#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from log import log

log = log('/webcrate/meta/webcrate.log')

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
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

for projectname,project in projects.items():
  project.name = projectname

  if hasattr(project, 'volume'):
    project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
  else:
    project.folder = f'/projects/{project.name}'

  UID = project.uid
  GID = project.uid

  if WEBCRATE_MODE == 'DEV':
    UID = WEBCRATE_UID
    GID = WEBCRATE_GID
  log.write(f'Create user and group for {project.name}')
  os.system(f'groupadd --non-unique --gid {GID} {project.name}')
  os.system(f'useradd --non-unique --no-create-home --uid {UID} --gid {GID} --home-dir {project.folder} {project.name}')
  os.system(f'usermod -s /bin/fish {project.name} > /dev/null 2>&1')
  os.system(f'chown {project.name}:{project.name} {project.folder}')
  password = str(project.password).replace("$", "\$")
  os.system(f'usermod -p {password} {project.name} > /dev/null 2>&1')

  print(f'{project.name} - created')
