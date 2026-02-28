#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/projects.yml', 'r') as f:
  content = f.read().strip()
  projects = munchify(yaml.safe_load(content)) if content else {}
  f.close()

WEBCRATE_PROJECT = os.environ.get('WEBCRATE_PROJECT', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

for projectname,project in projects.items():
  project.name = projectname
  if WEBCRATE_PROJECT == project.name:
    project.folder = f'/home/{project.name}'
    os.system(f'usermod -u {WEBCRATE_UID} dev > /dev/null 2>&1')
    os.system(f'usermod -l {project.name} dev > /dev/null 2>&1')
    os.system(f'groupmod -g {WEBCRATE_GID} dev > /dev/null 2>&1')
    os.system(f'groupmod --new-name {project.name} dev > /dev/null 2>&1')
    os.system(f'usermod -d /home/{project.name} {project.name} > /dev/null 2>&1')
    os.system(f'rm -r /home/dev > /dev/null 2>&1')
    os.system(f'chown -R {project.name}:{project.name} /run > /dev/null 2>&1')
    password = str(project.password).replace("$", "\\$")
    os.system(f'usermod -p {password} {project.name} > /dev/null 2>&1')
    os.system(f'mkdir -p /run/sshd > /dev/null 2>&1')
    os.system(f'chown root:root /run/sshd > /dev/null 2>&1')
    log.write(f'{project.name} - created', log.LEVEL.debug)
