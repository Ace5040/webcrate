#!/usr/bin/env python3

import os
import sys
import log
from log import log
log = log('/webcrate/log/app.log')
REDIRECT_NAME = sys.argv[1]

log.write(f'{REDIRECT_NAME} - run redirect config', log.LEVEL.debug)
os.system(f'docker exec webcrate-utils-docker /redirect-config.py {REDIRECT_NAME}')
log.write(f'{REDIRECT_NAME} - redirect config done', log.LEVEL.debug)
log.write(f'{REDIRECT_NAME} - run redirect start', log.LEVEL.debug)
os.system(f'docker exec webcrate-utils-docker /redirect-start.py {REDIRECT_NAME}')
log.write(f'{REDIRECT_NAME} - run redirect started', log.LEVEL.debug)

log.write(f'{REDIRECT_NAME} - reload nginx config', log.LEVEL.debug)
os.system(f'docker exec webcrate-nginx nginx -s reload')
log.write(f'{REDIRECT_NAME} - nginx config reloaded', log.LEVEL.debug)
log.write(f'{REDIRECT_NAME} - reload dnsmasq config', log.LEVEL.debug)
os.system(f'docker exec webcrate-dnsmasq kill -s SIGHUP 1')
log.write(f'{REDIRECT_NAME} - dnsmasq config reloaded', log.LEVEL.debug)

sys.exit(0)
