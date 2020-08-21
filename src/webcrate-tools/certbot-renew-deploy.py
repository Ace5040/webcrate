#!/usr/bin/env python3

import os
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

print(f'reload nginx config after certificates renewal')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/letsencrypt')
os.system(f'docker exec webcrate-nginx nginx -s reload')
