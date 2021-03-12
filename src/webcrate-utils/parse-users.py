#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify
from pprint import pprint
import json

with open('/webcrate/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
UID_START_NUMBER = 100000
CGI_PORT_START_NUMBER = 9000

#clean up configs
os.system(f'rm /webcrate/ssl_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/redirect_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/options_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/block_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/auth_locations_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/gzip_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php56-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php73-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php74-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php80-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate-dnsmasq/config/* > /dev/null 2>&1')

print(f'WEBCRATE_MODE = {WEBCRATE_MODE}')

for username, user in users.items():
  user.name = username
  data_folder=user.root_folder.split("/")[0]
  port = CGI_PORT_START_NUMBER + user.uid - UID_START_NUMBER

  if not os.path.isdir(f'/sites/{user.name}'):
    os.system(f'mkdir -p /sites/{user.name}')
  os.system(f'chown {WEBCRATE_UID if WEBCRATE_MODE == "DEV" else user.uid }:{WEBCRATE_GID if WEBCRATE_MODE == "DEV" else user.uid } /sites/{user.name}')
  os.system(f'chmod 0770 /sites/{user.name}')

  if not os.path.isdir(f'/sites/{user.name}/{user.root_folder}'):
    os.system(f'mkdir -p /sites/{user.name}/{user.root_folder}')
    if user.backend == 'php':
      with open(f'/sites/{user.name}/{user.root_folder}/index.php', 'w') as f:
        f.write(f'<?php\n')
        f.write(f'print "Welcome to webcrate. Happy coding!";\n')
        f.close()
    if user.backend == 'gunicorn':
      with open(f'/sites/{user.name}/{data_folder}/app.py', 'w') as f:
        f.write(f'def app(environ, start_response):\n'
        f'  data = b"Welcome to webcrate. Happy coding!"\n'
        f'  start_response("200 OK", [\n'
        f'  ("Content-Type", "text/plain"),\n'
        f'  ("Content-Length", str(len(data)))\n'
        f'  ])\n'
        f'  return iter([data])\n')
        f.close()
      os.system(f'cd /sites/{user.name}/{data_folder}; python -m venv env; source ./env/bin/activate; pip install gunicorn; pip freeze > requirements.txt; deactivate')
    os.system(f'chown -R {WEBCRATE_UID if WEBCRATE_MODE == "DEV" else user.uid }:{WEBCRATE_GID if WEBCRATE_MODE == "DEV" else user.uid } /sites/{user.name}/{data_folder}')

  if not os.path.isdir(f'/sites/{user.name}/log'):
    os.system(f'mkdir -p /sites/{user.name}/log')
    os.system(f'chown -R {WEBCRATE_UID if WEBCRATE_MODE == "DEV" else user.uid }:{WEBCRATE_GID if WEBCRATE_MODE == "DEV" else user.uid } /sites/{user.name}/log')

  if not os.path.isdir(f'/sites/{user.name}/tmp'):
    os.system(f'mkdir -p /sites/{user.name}/tmp')
    os.system(f'chown -R {WEBCRATE_UID if WEBCRATE_MODE == "DEV" else user.uid }:{WEBCRATE_GID if WEBCRATE_MODE == "DEV" else user.uid } /sites/{user.name}/tmp')

  if os.path.isdir(f'/sites/{user.name}'):
    if user.backend == 'php':
      php_path_prefix = {
        '56': '56',
        '73': '73',
        '74': '74'
      }.get(str(user.backend_version), '')
      php_conf_path = f'/webcrate/php{user.backend_version}-fpm.d/{user.name}.conf';

      if os.path.isfile(f'/webcrate/custom_templates/{user.name}.conf'):
        os.system(f'cp -rf /webcrate/custom_templates/{user.name}.conf {php_conf_path}')
      else:
        os.system(f'cp -rf /webcrate/custom_templates/php{user.backend_version}-default.conf {php_conf_path}')

      with open(php_conf_path, 'r') as f:
        conf = f.read()
        f.close()

      conf = conf.replace('%port%', str(port))
      conf = conf.replace('%user%', 'dev' if WEBCRATE_MODE=='DEV' else user.name)
      conf = conf.replace('%group%', 'dev' if WEBCRATE_MODE=='DEV' else user.name)
      conf = conf.replace('%path%', user.name)
      conf = conf.replace('%pool%', user.name)

      with open(php_conf_path, 'w') as f:
        f.write(conf)
        f.close()

      print(f'php pool for {user.name} - generated')

    with open(f'/sites/{user.name}/config.sh', 'w') as f:
      if user.backend == 'php':
        f.write(f'PATH=/webcrate-bin/php{php_path_prefix}:$PATH\n')
        f.write(f'PATH=/sites/{user.name}/.config/composer/vendor/bin:$PATH\n')
        f.write(f'PATH=/sites/{user.name}/{data_folder}/vendor/bin:$PATH\n')
        f.write(f'export COMPOSER_HOME=/sites/{user.name}/.config/composer\n')
        f.write(f'export DRUSH_PHP=/webcrate-bin/php{php_path_prefix}/php\n')
      f.write(f'export DATA_FOLDER={data_folder}\n')
      f.close()

    with open(f'/sites/{user.name}/config.fish', 'w') as f:
      if user.backend == 'php':
        f.write(f'set PATH /webcrate-bin/php{php_path_prefix} $PATH\n')
        f.write(f'set PATH /sites/{user.name}/.config/composer/vendor/bin $PATH\n')
        f.write(f'set PATH /sites/{user.name}/{data_folder}/vendor/bin $PATH\n')
        f.write(f'set -x COMPOSER_HOME /sites/{user.name}/.config/composer\n')
        f.write(f'set -x DRUSH_PHP /webcrate-bin/php{php_path_prefix}/php\n')
      f.write(f'set -x DATA_FOLDER {data_folder}\n')
      f.close()

    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /sites/{user.name}/config.sh')
    os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /sites/{user.name}/config.fish')

    conf = ''
    template = f'default-{user.backend}' if user.nginx_template == 'default' else f'default-{user.nginx_template}'
    if os.path.isfile(f'/webcrate/nginx-templates/{user.name}.conf'):
      template = user.name
    if os.path.isfile(f'/webcrate/nginx-templates/{template}.conf'):
      with open(f'/webcrate/nginx-templates/{template}.conf', 'r') as f:
        conf = f.read()
        f.close()

    conf = conf.replace('%user%', user.name)
    conf = conf.replace('%domains%', " ".join(user.domains))
    conf = conf.replace('%port%', str(port))
    conf = conf.replace('%root_folder%', user.root_folder)

    with open(f'/webcrate/nginx_configs/{user.name}.conf', 'w') as f:
      f.write(conf)
      f.close()

    print(f'nginx config for {user.name} - generated')

    if user.redirect:
      with open(f'/webcrate/redirect.conf', 'r') as f:
        conf = f.read()
        f.close()
      conf = conf.replace('%main-domain%', user.domains[0])
      with open(f'/webcrate/redirect_configs/{user.name}.conf', 'w') as f:
        f.write(conf)
        f.close()
      print(f'redirect config for {user.name} - generated')

    if user.nginx_options:
      with open(f'/webcrate/options_configs/{user.name}.conf', 'w') as f:
        for name, value in user.nginx_options.items():
          f.write(f'{name} {value};\n')
        f.close()
      print(f'nginx options config for {user.name} - generated')

    if user.nginx_block:
      with open(f'/webcrate/block_configs/{user.name}.conf', 'w') as f:
        f.write(user.nginx_block)
        f.close()
      print(f'nginx block config for {user.name} - generated')

    if user.auth_locations:
      with open(f'/webcrate/auth_locations_configs/{user.name}.conf', 'w') as f:
        index = 0
        for auth_location in user.auth_locations:
          index = index + 1
          f.write(
            f'location {auth_location.path} {{\n'
            f'  auth_basic "{auth_location.title}";\n'
            f'  auth_basic_user_file /webcrate/auth_locations_configs/{user.name}-{index}.password;\n'
            f'}}\n\n'
          )
          with open(f'/webcrate/auth_locations_configs/{user.name}-{index}.password', 'w') as pf:
            pf.write(f'{auth_location.user}:{auth_location.password}\n')
            pf.close()
        f.close()
      print(f'nginx options config for {user.name} - generated')

    if user.gzip:
      with open(f'/webcrate/gzip.conf', 'r') as f:
        conf = f.read()
        f.close()
      with open(f'/webcrate/gzip_configs/{user.name}.conf', 'w') as f:
        f.write(conf)
        f.close()
      print(f'gzip config for {user.name} - generated')

    if user.https == 'letsencrypt':
      if os.path.isdir(f'/webcrate/letsencrypt/live/{user.name}'):
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', 'letsencrypt')
        conf = conf.replace('%path%', f'live/{user.name}')
        with open(f'/webcrate/ssl_configs/{user.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        print(f'ssl config for {user.name} - generated')

    if user.https == 'openssl':
      if os.path.isdir(f'/webcrate/openssl/{user.name}'):
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%type%', 'openssl')
        conf = conf.replace('%path%', f'{user.name}')
        with open(f'/webcrate/ssl_configs/{user.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        print(f'ssl config for {user.name} - generated')


if WEBCRATE_MODE == "DEV":
  with open(f'/webcrate-dnsmasq/config/hosts_nginx', 'w') as f:
    for username, user in users.items():
      user.name = username
      f.write(f'{DOCKER_HOST_IP} {" ".join(user.domains)}\n')
    f.close()

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/ssl_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/options_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/auth_locations_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/redirect_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/gzip_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php56-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php73-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php74-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php80-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate-dnsmasq/config')
sys.stdout.flush()