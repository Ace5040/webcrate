#!/usr/bin/env python3

import sys
import json
import subprocess

PREFIX = 'webcrate-core-'

containers_raw = subprocess.run(
  ['docker', 'ps', '--format', '{{.Names}}', '--filter', f'name={PREFIX}'],
  capture_output=True, text=True
).stdout.strip()

containers = [line for line in containers_raw.splitlines() if line.startswith(PREFIX)]

all_soft = {}
for container in containers:
  key = container[len(PREFIX):]
  raw = subprocess.run(
    ['docker', 'exec', container, '/webcrate/versions.py'],
    capture_output=True, text=True
  ).stdout.strip()
  try:
    all_soft[key] = json.loads(raw)
  except json.JSONDecodeError:
    all_soft[key] = {}

sys.stdout.write(json.dumps(all_soft))
sys.stdout.flush()
sys.exit(0)
