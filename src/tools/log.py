#!/usr/bin/env python3
import sys
import os

class log:

  path: ''

  def __init__(self, path):
    self.path = path

  def write(self, text):
    if self.path == '':
      print('File path is empty')
    else:
      try:
        f = open(self.path, 'a')
      except OSError:
        print(f'Could not open/create file: {self.path}')
        sys.exit()
      with f:
        date = os.popen(f'date -Is | tr -d \'\\n\'').read().strip()
        f.write(f'{date}:: {text}\n')
        f.close()
