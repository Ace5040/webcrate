#!/usr/bin/env python3

import os

print(f'reload nginx config after certificates renewal')
os.system(f'docker exec webcrate-nginx nginx -s reload')
