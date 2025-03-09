#!/usr/bin/env python3
import sys
import os
from enum import IntEnum

class LEVEL(IntEnum):
	debug = 8
	info = 6
	error = 3

class log:

	path = ''
	LOG_LEVEL_VALUE = int(os.environ.get('LOG_LEVEL_VALUE', 3))
	LEVEL = LEVEL

	def __init__(self, path):
		self.path = path

	def write(self, text, level):
		if self.path == '':
			print('File path is empty')
		else:
			try:
				f = open(self.path, 'a')
			except OSError:
				print(f'Could not open/create file: {self.path}')
				sys.exit()
			with f:
				if self.LOG_LEVEL_VALUE >= int(level):
					date = os.popen(f'date -Is | tr -d \'\\n\'').read().strip()
					f.write(f'{date}:: {text}\n')
					print(f'{date}:: {text}\n')
					f.close()
