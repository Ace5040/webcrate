#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

os.system(f'userdel dev > /dev/null 2>&1')

for projectname,project in projects.items():
  project.name = projectname
  project.folder = f'/home/{project.name}'

  log.write(f'Create user and group for {project.name}')
  os.system(f'groupadd --non-unique --gid {WEBCRATE_GID} {project.name}')
  os.system(f'useradd --non-unique --no-create-home --uid {WEBCRATE_UID} --gid {WEBCRATE_GID} --home-dir {project.folder} {project.name}')
  os.system(f'usermod -s /bin/nologin {project.name} > /dev/null 2>&1')
  password = str(project.password).replace("$", "\\$")
  os.system(f'usermod -p {password} {project.name} > /dev/null 2>&1')
  os.system(f'touch /etc/ftp.passwd')
  if hasattr(project, 'ftps') and project.ftps:
    log.write(f'Create ftp accounts for {project.name}')
    with open(f'/etc/ftp.passwd', 'a') as f:
      for ftp in project.ftps:
        ftp_folder = f'{project.folder}{("/" + ftp.home) if ftp.home else ""}'
        f.write(f'{ftp.name}:{ftp.password}:{WEBCRATE_UID}:{WEBCRATE_GID}::{ftp_folder}:/bin/false\n')
        os.system(f'mkdir -p {ftp_folder}')
        os.system(f'chown -R {project.name}:{project.name} {ftp_folder}')
      f.close()

    print(f'additional ftp accounts for {project.name} - generated')
  os.system(f'chmod a-rwx,u+rw /etc/ftp.passwd')
  print(f'{project.name} - created')
