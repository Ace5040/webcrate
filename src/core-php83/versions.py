#!/usr/bin/env python3

import os
import yaml
import time
import json
from munch import munchify
from pprint import pprint

def execCommand(cmd):
  return os.popen(f'{cmd} | tr -d \'\\n\'').read().strip()

php = execCommand("php -v | awk 'NR<=1{ print $2 }'")
composer = execCommand("composer -V | awk 'NR<=1{ print $3 }'")
mise = execCommand("mise version --json | awk -F'\"' '/\"version\"/{split($4, a, \" \"); print a[1]}'")
git = execCommand("git --version | awk 'NR<=1{ print $3 }'")
symfony = execCommand("symfony -V | awk 'NR<=1{ print $4 }' | sed -r 's/\x1B\[([0-9]{1,3}(;[0-9]{1,2})?)?[mGK]//g' | tr -d 'v'")
compass = execCommand("compass -v | awk 'NR<=1{ print $2 }'")
python = execCommand("python -V | awk 'NR<=1{ print $2 }'")
pip = execCommand("pip -V | awk 'NR<=1{ print $2 }'")
gem = execCommand("gem -v | awk 'NR<=1{ print $1 }'")
tmux = execCommand("tmux -V | awk 'NR<=1{ print $2 }'")
soft = [
    dict( name = 'php', version = php ),
    dict( name = 'composer', version = composer ),
    dict( name = 'mise', version = mise ),
    dict( name = 'git', version = git ),
    dict( name = 'symfony cli', version = symfony ),
    dict( name = 'compass', version = compass ),
    dict( name = 'python', version = python ),
    dict( name = 'pip', version = pip ),
    dict( name = 'gem', version = gem ),
    dict( name = 'tmux', version = tmux )
]
print(json.dumps(soft))
