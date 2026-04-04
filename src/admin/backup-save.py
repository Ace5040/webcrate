#!/usr/bin/env python3

import os
import sys
from log import log

log = log('/webcrate/log/app.log')
PROJECT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'all'
BACKUP_TIME = sys.argv[2] if len(sys.argv) > 2 else ''
MAKE_ARCHIVE = sys.argv[3] if len(sys.argv) > 3 else ''

log.write(f'Saving backup: {PROJECT_NAME} {BACKUP_TIME}', log.LEVEL.debug)
cmd = f'docker exec webcrate-utils-docker /backup-save.py {PROJECT_NAME} {BACKUP_TIME}'
if MAKE_ARCHIVE:
    cmd += f' {MAKE_ARCHIVE}'
os.system(cmd)
log.write(f'Save backup finished: {PROJECT_NAME} {BACKUP_TIME}', log.LEVEL.debug)
sys.exit(0)
