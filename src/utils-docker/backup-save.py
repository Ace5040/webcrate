#!/usr/bin/env python3

import os
import sys
import yaml
import tarfile
import subprocess
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')
log.write(f'Starting backup-save process', log.LEVEL.debug)

with open('/webcrate/projects.yml', 'r') as f:
  content = f.read().strip()
  projects = munchify(yaml.safe_load(content)) if content else {}
  f.close()

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
WEBCRATE_BACKUP_URIS = os.environ.get('WEBCRATE_BACKUP_URIS', '') or 'file:///webcrate/backup'
BACKUP_URIS = WEBCRATE_BACKUP_URIS.split('^')
PROJECT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'all'
BACKUP_TIME = sys.argv[2] if len(sys.argv) > 2 else None
MAKE_ARCHIVE = sys.argv[3] == 'archive' if len(sys.argv) > 3 else False

if not BACKUP_TIME:
  log.write(f'Error: backup time not specified (sys.argv[2])', log.LEVEL.debug)
  sys.exit(1)

BACKUP_URI = BACKUP_URIS[0]
# Use time as directory/archive name, replacing colons for filesystem safety
BACKUP_LABEL = BACKUP_TIME.replace(':', '-')

def restore(source_uri, target_dir):
  os.makedirs(target_dir, exist_ok=True)
  log.write(f'Restoring {source_uri} -> {target_dir} at {BACKUP_TIME}', log.LEVEL.debug)
  subprocess.run([
    'duplicity', 'restore',
    '--verbosity', 'notice',
    '--no-encryption',
    '--time', BACKUP_TIME,
    '--archive-dir', '/webcrate/duplicity/.duplicity',
    '--log-file', '/webcrate/duplicity/duplicity.log',
    '--force',
    source_uri,
    target_dir,
  ])
  sys.stdout.flush()

def make_archive(source_dir, archive_path):
  log.write(f'Creating archive {archive_path}', log.LEVEL.debug)
  with tarfile.open(archive_path, 'w:gz') as tar:
    tar.add(source_dir, arcname=os.path.basename(source_dir))
  subprocess.run(['rm', '-rf', source_dir])

def restore_project(project_name, project_folder, project):
  backups_dir = f'{project_folder}/backups/{BACKUP_LABEL}'

  restore(f'{BACKUP_URI}/projects/{project_name}/files', f'{backups_dir}/files')

  if os.path.isdir(f'{project_folder}/var/solr/cores'):
    restore(f'{BACKUP_URI}/projects/{project_name}/solr-cores', f'{backups_dir}/solr-cores')

  if project.mysql_db:
    restore(f'{BACKUP_URI}/projects/{project_name}/project-mysql', f'{backups_dir}/project-mysql')

  if project.mysql5_db:
    restore(f'{BACKUP_URI}/projects/{project_name}/project-mysql5', f'{backups_dir}/project-mysql5')

  if project.postgresql_db:
    restore(f'{BACKUP_URI}/projects/{project_name}/project-postgresql', f'{backups_dir}/project-postgresql')

  if MAKE_ARCHIVE:
    make_archive(backups_dir, f'{project_folder}/backups/{BACKUP_LABEL}.tar.gz')
    subprocess.run(['chown', f'{WEBCRATE_UID}:{WEBCRATE_GID}', f'{project_folder}/backups/{BACKUP_LABEL}.tar.gz'])
  else:
    subprocess.run(['chown', '-R', f'{WEBCRATE_UID}:{WEBCRATE_GID}', backups_dir])
  os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project_folder}/backups')

# restore webcrate admin
if PROJECT_NAME == 'admin' or PROJECT_NAME == 'all':
  admin_backups_dir = f'/webcrate/backups/{BACKUP_LABEL}'
  restore(f'{BACKUP_URI}/webcrate/files', f'{admin_backups_dir}/files')
  restore(f'{BACKUP_URI}/webcrate/mysql', f'{admin_backups_dir}/mysql')
  if MAKE_ARCHIVE:
    make_archive(admin_backups_dir, f'/webcrate/backups/{BACKUP_LABEL}.tar.gz')
    subprocess.run(['chown', f'{WEBCRATE_UID}:{WEBCRATE_GID}', f'/webcrate/backups/{BACKUP_LABEL}.tar.gz'])
  else:
    subprocess.run(['chown', '-R', f'{WEBCRATE_UID}:{WEBCRATE_GID}', admin_backups_dir])

# restore projects
for projectname, project in projects.items():
  project.name = projectname
  if project.backup and project.active and (PROJECT_NAME == projectname or PROJECT_NAME == 'all'):
    if hasattr(project, 'volume'):
      project_folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
    else:
      project_folder = f'/projects/{project.name}'
    restore_project(project.name, project_folder, project)

log.write(f'Backup-save process ended', log.LEVEL.debug)
sys.stdout.flush()
