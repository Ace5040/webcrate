#!/usr/bin/env python3

import os
import sys

PROJECT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'all'
os.system(f'docker exec webcrate-utils-docker /backup-list.py {PROJECT_NAME}')
sys.exit(0)
