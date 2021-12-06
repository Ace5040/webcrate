#!/usr/bin/env python3

import os
import sys

WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

#parse projects
os.system(f'/webcrate/parse-projects.py')
print(f'projects parsed')
sys.stdout.flush()

#reload nginx service
os.system(f'nginx -s reload')
print(f'nginx service reloaded')
sys.stdout.flush()
