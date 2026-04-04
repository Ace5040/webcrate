#!/usr/bin/env python3

import os
import re
import sys
import json
import yaml
import subprocess
from datetime import datetime
from munch import munchify
from log import log

log = log('/webcrate/log/app.log')

with open('/webcrate/projects.yml', 'r') as f:
  content = f.read().strip()
  projects = munchify(yaml.safe_load(content)) if content else {}
  f.close()

WEBCRATE_BACKUP_URIS = os.environ.get('WEBCRATE_BACKUP_URIS', '') or 'file:///webcrate/backup'
BACKUP_URIS = WEBCRATE_BACKUP_URIS.split('^')
PROJECT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'all'

def fmt_date(s):
  if not s:
    return s
  try:
    return datetime.strptime(' '.join(s.split()), '%a %b %d %H:%M:%S %Y').strftime('%Y-%m-%dT%H:%M:%S')
  except ValueError:
    return s

def collection_status(uri):
  result = subprocess.run(
    [
      'duplicity',
      '--verbosity', 'notice',
      '--no-encryption',
      '--archive-dir', '/webcrate/duplicity/.duplicity',
      '--log-file', '/webcrate/duplicity/duplicity.log',
      'collection-status',
      uri,
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
  )
  return parse_collection_status(result.stdout + result.stderr)

def parse_collection_status(output):
  chains = []
  current_chain = None
  in_sets_table = False

  for line in output.splitlines():
    line = line.strip()

    m = re.match(r'Chain start time:\s+(.+)', line)
    if m:
      current_chain = {'start': fmt_date(m.group(1).strip()), 'end': None, 'sets': []}
      chains.append(current_chain)
      in_sets_table = False
      continue

    m = re.match(r'Chain end time:\s+(.+)', line)
    if m and current_chain is not None:
      current_chain['end'] = fmt_date(m.group(1).strip())
      continue

    if re.match(r'Type of backup set:', line):
      in_sets_table = True
      continue

    if in_sets_table and current_chain is not None:
      m = re.match(r'(Full|Incremental)\s+(.+\d{4})\s+(\d+)\s*$', line)
      if m:
        current_chain['sets'].append({
          'type': m.group(1),
          'time': fmt_date(m.group(2).strip()),
          'volumes': int(m.group(3)),
        })
        continue
      if line.startswith('---') or line == '':
        in_sets_table = False

  return chains

result = {}

for BACKUP_URI in BACKUP_URIS:
  result[BACKUP_URI] = {}

  # webcrate admin
  if PROJECT_NAME == 'admin' or PROJECT_NAME == 'all':
    result[BACKUP_URI]['webcrate'] = {
      'files': collection_status(f'{BACKUP_URI}/webcrate/files'),
      'mysql': collection_status(f'{BACKUP_URI}/webcrate/mysql'),
    }

  # projects
  result[BACKUP_URI]['projects'] = {}
  for projectname, project in projects.items():
    project.name = projectname
    if project.backup and project.active and (PROJECT_NAME == projectname or PROJECT_NAME == 'all'):
      project_result = {}

      project_result['files'] = collection_status(f'{BACKUP_URI}/projects/{project.name}/files')

      if hasattr(project, 'volume'):
        project_folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
      else:
        project_folder = f'/projects/{project.name}'

      if os.path.isdir(f'{project_folder}/var/solr/cores'):
        project_result['solr-cores'] = collection_status(f'{BACKUP_URI}/projects/{project.name}/solr-cores')

      if project.mysql_db:
        project_result['project-mysql'] = collection_status(f'{BACKUP_URI}/projects/{project.name}/project-mysql')

      if project.mysql5_db:
        project_result['project-mysql5'] = collection_status(f'{BACKUP_URI}/projects/{project.name}/project-mysql5')

      if project.postgresql_db:
        project_result['project-postgresql'] = collection_status(f'{BACKUP_URI}/projects/{project.name}/project-postgresql')

      result[BACKUP_URI]['projects'][project.name] = project_result

print(json.dumps(result, indent=2))
