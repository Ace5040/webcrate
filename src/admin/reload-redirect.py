#!/usr/bin/env python3

import os
import sys

REDIRECT_NAME = sys.argv[1]

os.system(f'docker exec webcrate-tools /webcrate/scripts/redirect-config.py {REDIRECT_NAME}')
os.system(f'docker exec webcrate-tools /webcrate/scripts/redirect-certs.py {REDIRECT_NAME}')
os.system(f'docker exec webcrate-nginx nginx -s reload')

sys.exit(0)
