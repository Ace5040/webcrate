#!/usr/bin/env python3

import os

os.system(f'docker exec webcrate-nginx nginx -s reload')
