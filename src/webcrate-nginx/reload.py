#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

#delete groups
with open("/etc/group") as file:
  for line in file:
    arr=line.split(":")
    group_name = arr[0]
    group_id = int(arr[2])
    if ( ( WEBCRATE_MODE == 'DEV' and group_id == int(WEBCRATE_GID) ) or ( WEBCRATE_MODE == 'PRODUCTION' and group_id >= 100000 ) ) and group_id != 0:
      os.system(f'groupdel -f {group_name} >/dev/null 2>/dev/null')
print(f'groups deleted')
sys.stdout.flush()

#parse projects
os.system(f'/webcrate/parse-projects.py')
print(f'projects parsed')
sys.stdout.flush()

#reload nginx service
os.system(f'nginx -s reload')
print(f'nginx service reloaded')
sys.stdout.flush()
