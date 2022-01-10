#!/usr/bin/env python3

import os
import sys

PROJECT_NAME = sys.argv[1]

os.system(f'for i in `docker network inspect -f "{{{{range .Containers}}}}{{{{.Name}}}} {{{{end}}}}" webcrate_network_{PROJECT_NAME}`; do docker network disconnect -f webcrate_network_{PROJECT_NAME} $i; done;')
os.system(f'docker network rm webcrate_network_{PROJECT_NAME}')
os.system(f'containers=$(docker ps -a -q --filter name=webcrate-{PROJECT_NAME}-); if [ "$containers" != "" ]; then docker stop $containers > /dev/null; docker container rm $containers > /dev/null; fi')
os.system(f'containers=$(docker ps -a -q --filter name=webcrate-core-{PROJECT_NAME}); if [ "$containers" != "" ]; then docker stop $containers > /dev/null; docker container rm $containers > /dev/null; fi')
os.system(f'docker exec webcrate-tools /webcrate/project-config.py {PROJECT_NAME}')
os.system(f'docker exec webcrate-tools /webcrate/project-start.py {PROJECT_NAME}')
os.system(f'docker exec webcrate-nginx nginx -s reload')

sys.exit(0)
