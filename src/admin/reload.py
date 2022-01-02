#!/usr/bin/env python3

import os
import sys

#os.system(f'docker exec webcrate-tools /webcrate/parse-projects.py')
#os.system(f'docker exec webcrate-tools /webcrate/parse-services.py')
#os.system(f'docker exec webcrate-tools /webcrate/parse-configs.py')
#os.system(f'docker exec webcrate-core-php /webcrate/reload.py')
os.system(f'docker exec webcrate-nginx /webcrate/reload.py')

sys.exit(0)
