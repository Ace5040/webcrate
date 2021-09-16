#!/usr/bin/env python3

import os
from log import log

log = log('/webcrate/meta/webcrate.log')

log.write(f'Deploy new certificates')

os.system(f'docker exec webcrate-nginx nginx -s reload')
