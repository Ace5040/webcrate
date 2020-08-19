#!/usr/bin/env python3

import os
import yaml
from munch import munchify
from pprint import pprint

with open('/webcrate/users/users.yml', 'r') as f:
  users = munchify(yaml.safe_load(f))

MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
UID_START_NUMBER = int(os.environ.get('UID_START_NUMBER', '100000'))
CGI_PORT_START_NUMBER = int(os.environ.get('CGI_PORT_START_NUMBER', '9000'))

#clean up configs
os.system(f'rm /webcrate/ssl_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx_configs/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php73-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate/php56-fpm.d/* > /dev/null 2>&1')
os.system(f'rm /webcrate/dnsmasq_hosts/* > /dev/null 2>&1')

print(f'MODE = {MODE}')

for username, user in users.items():
  user.name = username
  port = CGI_PORT_START_NUMBER + user.uid - UID_START_NUMBER

  if os.path.isdir(f'/sites/{user.name}'):
    if user.backend == 'php':
      php_path_prefix = {
        '5': '56',
        '73': '73',
      }.get(str(user.backend_version), '')
      php_conf_path = f'/webcrate/php{php_path_prefix}-fpm.d/{user.name}.conf';
      os.system(f'cp -rf /webcrate/custom_templates/php{user.backend_version}-default.conf {php_conf_path}')

      with open(php_conf_path, 'r') as f:
        conf = f.read()
        f.close()

      conf = conf.replace('%port%', str(port))
      conf = conf.replace('%user%', 'dev' if MODE=='DEV' else user.name)
      conf = conf.replace('%group%', 'dev' if MODE=='DEV' else user.name)
      conf = conf.replace('%path%', user.name)
      conf = conf.replace('%pool%', user.name)

      with open(php_conf_path, 'w') as f:
        f.write(conf)
        f.close()

      with open(f'/sites/{user.name}/phpversion.sh', 'w') as f:
        f.write(f'PATH=/webcrate/bin/php{php_path_prefix}:$PATH')
        f.close()

      with open(f'/sites/{user.name}/phpversion.fish', 'w') as f:
        f.write(f'set PATH /webcrate/bin/php{php_path_prefix} $PATH')
        f.close()

      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /sites/{user.name}/phpversion.sh')
      os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /sites/{user.name}/phpversion.fish')

      print(f'php pool for {user.name} - generated')

    os.system(f'cp -rf /webcrate/users/{user.name}.conf /webcrate/nginx_configs/{user.name}.conf')

    with open(f'/webcrate/nginx_configs/{user.name}.conf', 'r') as f:
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

    if user.https == 'letsencrypt':
      if os.path.isdir(f'/webcrate/letsencrypt/live/{user.name}'):
        with open(f'/webcrate/ssl.conf', 'r') as f:
          conf = f.read()
          f.close()
        conf = conf.replace('%user%', user.name)
        with open(f'/webcrate/ssl_configs/{user.name}.conf', 'w') as f:
          f.write(conf)
          f.close()
        print(f'ssl config for {user.name} - generated')

if MODE == "DEV":
  with open(f'/webcrate/dnsmasq_hosts/hosts_nginx', 'w') as f:
    for username, user in users.items():
      user.name = username
      f.write(f'{DOCKER_HOST_IP} {" ".join(user.domains)}\n')
    f.close()

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/ssl_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx_configs')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php73-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php56-fpm.d')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq_hosts')
