#!/usr/bin/env python3

import os
import sys
from log import log

log = log('/webcrate/log/app.log')
PROJECT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'all'

log.write(f'Starting backup: {PROJECT_NAME}', log.LEVEL.debug)
os.system(f'docker exec webcrate-utils-docker /backup.py {PROJECT_NAME}')
log.write(f'Backup finished: {PROJECT_NAME}', log.LEVEL.debug)
sys.exit(0)
