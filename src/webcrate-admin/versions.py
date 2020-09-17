#!/usr/bin/env python3

import os
import sys
import json

soft = os.popen(f'docker exec webcrate-core /webcrate/versions.py').read().strip()
sys.stdout.write(soft)
sys.stdout.flush()
sys.exit(0)
