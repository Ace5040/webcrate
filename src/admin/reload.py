#!/usr/bin/env python3

import os
import sys
import log
from log import log
log = log('/webcrate/log/app.log')
PROJECT_NAME = sys.argv[1]

log.write(f'{PROJECT_NAME} - disconnecting networks', log.LEVEL.debug)
os.system(f'for i in `docker network inspect -f "{{{{range .Containers}}}}{{{{.Name}}}} {{{{end}}}}" webcrate_network_{PROJECT_NAME}`; do docker network disconnect -f webcrate_network_{PROJECT_NAME} $i; done;')
log.write(f'{PROJECT_NAME} - networks disconnected', log.LEVEL.debug)
log.write(f'{PROJECT_NAME} - removing network', log.LEVEL.debug)
os.system(f'docker network rm webcrate_network_{PROJECT_NAME}')
log.write(f'{PROJECT_NAME} - network removed', log.LEVEL.debug)
log.write(f'{PROJECT_NAME} - stoping services containers', log.LEVEL.debug)
os.system(f'containers=$(docker ps -a -q --filter name=webcrate-{PROJECT_NAME}-); if [ "$containers" != "" ]; then docker stop $containers > /dev/null; docker container rm $containers > /dev/null; fi')
log.write(f'{PROJECT_NAME} - services containers stopped', log.LEVEL.debug)
log.write(f'{PROJECT_NAME} - stoping core container', log.LEVEL.debug)
os.system(f'containers=$(docker ps -a -q --filter name=webcrate-core-{PROJECT_NAME}); if [ "$containers" != "" ]; then docker stop $containers > /dev/null; docker container rm $containers > /dev/null; fi')
log.write(f'{PROJECT_NAME} - core container stopped', log.LEVEL.debug)

log.write(f'{PROJECT_NAME} - run project config', log.LEVEL.debug)
os.system(f'docker exec webcrate-utils-docker /project-config.py {PROJECT_NAME} reload')
log.write(f'{PROJECT_NAME} - project config done', log.LEVEL.debug)
log.write(f'{PROJECT_NAME} - run project start', log.LEVEL.debug)
os.system(f'docker exec webcrate-utils-docker /project-start.py {PROJECT_NAME} reload')
log.write(f'{PROJECT_NAME} - run project started', log.LEVEL.debug)

log.write(f'{PROJECT_NAME} - reload nginx config', log.LEVEL.debug)
os.system(f'docker exec webcrate-nginx nginx -s reload')
log.write(f'{PROJECT_NAME} - nginx config reloaded', log.LEVEL.debug)
log.write(f'{PROJECT_NAME} - reload dnsmasq config', log.LEVEL.debug)
os.system(f'docker exec webcrate-dnsmasq kill -s SIGHUP 1')
log.write(f'{PROJECT_NAME} - dnsmasq config reloaded', log.LEVEL.debug)

sys.exit(0)
