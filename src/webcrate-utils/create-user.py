#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/users.yml', 'r') as f:
  users = yaml.safe_load(f)
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
UID_START_NUMBER = 100000
CGI_PORT_START_NUMBER = 9000
