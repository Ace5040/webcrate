#!/usr/bin/env python3

import os
import sys
import yaml
from munch import munchify
import json
import hashlib

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

DOCKER_HOST_IP = os.environ.get('DOCKER_HOST_IP', '')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')
UID_START_NUMBER = 100000
SSH_PORT_START_NUMBER = 10000

PROJECT_NAME = sys.argv[1]

#cleanup configs
os.system(f'rm /webcrate/nginx/ssl/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/redirect/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/options/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/block/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/auth/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/auth/{PROJECT_NAME}-*.password > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/gzip/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/nginx/confs/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/php_pools/{PROJECT_NAME}.conf > /dev/null 2>&1')
os.system(f'rm /webcrate/dnsmasq/hosts/{PROJECT_NAME}.hosts > /dev/null 2>&1')
os.system(f'rm /webcrate/meta/projects/{PROJECT_NAME}.config > /dev/null 2>&1')

for projectname,project in projects.items():
  if PROJECT_NAME == projectname:
    dump = json.dumps(project, separators=(',', ':'), ensure_ascii=True)
    if project.active:
      project.name = projectname
      project.full_backend_version = f'{project.backend}{project.backend_version}'

      data_folder=project.root_folder.split("/")[0]
      port = 9000
      ssh_port = SSH_PORT_START_NUMBER + project.uid - UID_START_NUMBER
      net_num = project.uid - UID_START_NUMBER
      domain = project.domains[0]

      if hasattr(project, 'volume'):
        project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
      else:
        project.folder = f'/projects/{project.name}'

      if not os.path.isdir(f'{project.folder}'):
        os.system(f'mkdir -p {project.folder}')
        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}')

      if not os.path.isdir(f'{project.folder}/{project.root_folder}'):
        os.system(f'mkdir -p {project.folder}/{project.root_folder}')
        if project.backend == 'php':
          with open(f'{project.folder}/{project.root_folder}/index.php', 'w') as f:
            f.write(f'<?php\n')
            f.write(f'print "Welcome to webcrate. Happy coding!";\n')
            f.close()
        if project.backend == 'gunicorn':
          os.system(f'touch {project.folder}/{data_folder}/gunicorn.init')
          path = "/".join(project.gunicorn_app_module.split(":")[0].split("."))
          app_name = project.gunicorn_app_module.split(":")[1]
          app_file_path = f'{project.folder}/{data_folder}/{path}.py'
          app_file_dir = os.path.dirname(os.path.abspath(app_file_path))
          if not os.path.isdir(f'{app_file_dir}'):
            os.system(f'mkdir -p {app_file_dir}')
          with open(f'{app_file_path}', 'w') as f:
            f.write(f'def { app_name if app_name else "app"}(environ, start_response):\n'
            f'  data = b"Welcome to webcrate. Happy coding!"\n'
            f'  start_response("200 OK", [\n'
            f'  ("Content-Type", "text/plain"),\n'
            f'  ("Content-Length", str(len(data)))\n'
            f'  ])\n'
            f'  return iter([data])\n')
            f.close()
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/{data_folder}')

      if not os.path.isdir(f'{project.folder}/log'):
        os.system(f'mkdir -p {project.folder}/log')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/log')

      if not os.path.isdir(f'{project.folder}/supervisor/conf.d'):
        os.system(f'mkdir -p {project.folder}/supervisor/conf.d')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/supervisor')

      if not os.path.isdir(f'{project.folder}/exim-spool'):
        os.system(f'mkdir -p {project.folder}/exim-spool')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/exim-spool')

      if not os.path.isdir(f'{project.folder}/tmp'):
        os.system(f'mkdir -p {project.folder}/tmp')
        os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/tmp')

      if os.path.isdir(f'{project.folder}'):
        if project.backend == 'php':
          php_path_prefix = {
            '81': '81',
            '56': '56',
            '73': '73',
            '74': '74'
          }.get(str(project.backend_version), '81')
          php_conf_path = f'/webcrate/php_pools/{project.name}.conf';

          if os.path.isfile(f'/webcrate/custom_templates/{project.name}.conf'):
            os.system(f'cp -rf /webcrate/custom_templates/{project.name}.conf {php_conf_path}')
          else:
            os.system(f'cp -rf /webcrate/custom_templates/php{php_path_prefix}-default.conf {php_conf_path}')

          with open(php_conf_path, 'r') as f:
            conf = f.read()
            f.close()

          conf = conf.replace('%port%', str(port))
          conf = conf.replace('%user%', project.name)
          conf = conf.replace('%group%', project.name)
          conf = conf.replace('%path%', f'/home/{project.name}')
          conf = conf.replace('%pool%', project.name)

          with open(php_conf_path, 'w') as f:
            f.write(conf)
            f.close()

          print(f'php pool for {project.name} - generated')

        with open(f'{project.folder}/config.sh', 'w') as f:
          if project.backend == 'php':
            f.write(f'PATH=/webcrate-bin:$PATH\n')
            f.write(f'PATH=/home/{project.name}/.config/composer/vendor/bin:$PATH\n')
            f.write(f'PATH=/home/{project.name}/{data_folder}/vendor/bin:$PATH\n')
            f.write(f'export COMPOSER_HOME=/home/{project.name}/.config/composer\n')
            f.write(f'export DRUSH_PHP=/webcrate-bin/php\n')
          f.write(f'export DATA_FOLDER={data_folder}\n')
          f.close()

        os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/config.sh')

        conf = ''
        template = f'default-{project.backend}' if project.nginx_template == 'default' else f'default-{project.nginx_template}'
        if os.path.isfile(f'/webcrate/nginx-templates/{project.name}.conf'):
          template = project.name
        if os.path.isfile(f'/webcrate/nginx-templates/{template}.conf'):
          with open(f'/webcrate/nginx-templates/{template}.conf', 'r') as f:
            conf = f.read()
            f.close()

        conf = conf.replace('%project%', project.name)
        conf = conf.replace('%domains%', " ".join(project.domains))
        conf = conf.replace('%port%', str(port))
        conf = conf.replace('%project_folder%', f'/home/{project.name}')
        conf = conf.replace('%root_folder%', project.root_folder)
        conf = conf.replace('%core%', f'webcrate-core-{project.name}')

        os.system(f'echo "{net_num} '
          f'{project.name} '
          f'{project.full_backend_version} '
          f'webcrate-core-{project.name} '
          f'{ssh_port} '
          f'{domain} '
          f'{project.password} '
          f'{project.memcached} '
          f'{project.solr}'
          f'" >> /webcrate/meta/projects/{project.name}.config')

        with open(f'/webcrate/nginx/confs/{project.name}.conf', 'w') as f:
          f.write(conf)
          f.close()

        print(f'nginx config for {project.name} - generated')

        if project.redirect:
          with open(f'/webcrate/redirect.conf', 'r') as f:
            conf = f.read()
            f.close()
          conf = conf.replace('%main-domain%', project.domains[0])
          with open(f'/webcrate/nginx/redirect/{project.name}.conf', 'w') as f:
            f.write(conf)
            f.close()
          print(f'redirect config for {project.name} - generated')

        if project.nginx_options:
          with open(f'/webcrate/nginx/options/{project.name}.conf', 'w') as f:
            for name, value in project.nginx_options.items():
              f.write(f'{name} {value};\n')
            f.close()
          print(f'nginx options config for {project.name} - generated')

        if project.nginx_block:
          with open(f'/webcrate/nginx/block/{project.name}.conf', 'w') as f:
            f.write(project.nginx_block)
            f.close()
          print(f'nginx block config for {project.name} - generated')

        if project.auth_locations:
          with open(f'/webcrate/nginx/auth/{project.name}.conf', 'w') as f:
            index = 0
            for auth_location in project.auth_locations:
              index = index + 1
              f.write(
                f'location ~ {auth_location.path}/.* {{\n'
                f'  auth_basic "{auth_location.title}";\n'
                f'  auth_basic_user_file /webcrate/nginx/auth/{project.name}-{index}.password;\n'
                f'  location ~ \.php$ {{\n'
                f'    fastcgi_split_path_info ^(.+?\.php)(|/.*)$;\n'
                f'    resolver 127.0.0.11 valid=60s;\n'
                f'    set $core webcrate-core-{project.name}:{ str(port) };\n'
                f'    fastcgi_pass $core;\n'
                f'    try_files $fastcgi_script_name =404;\n'
                f'    include fastcgi_params;\n'
                f'    fastcgi_read_timeout 60;\n'
                f'    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;\n'
                f'  }}\n'
                f'}}\n\n'
              )
              with open(f'/webcrate/nginx/auth/{project.name}-{index}.password', 'w') as pf:
                pf.write(f'{auth_location.user}:{auth_location.password}\n')
                pf.close()
            f.close()
          print(f'nginx options config for {project.name} - generated')

        if project.gzip:
          with open(f'/webcrate/gzip.conf', 'r') as f:
            conf = f.read()
            f.close()
          with open(f'/webcrate/nginx/gzip/{project.name}.conf', 'w') as f:
            f.write(conf)
            f.close()
          print(f'gzip config for {project.name} - generated')

        if project.https == 'letsencrypt':
          if os.path.isdir(f'/webcrate/letsencrypt/live/{project.name}'):
            with open(f'/webcrate/ssl.conf', 'r') as f:
              conf = f.read()
              f.close()
            conf = conf.replace('%type%', 'letsencrypt')
            conf = conf.replace('%path%', f'live/{project.name}')
            with open(f'/webcrate/nginx/ssl/{project.name}.conf', 'w') as f:
              f.write(conf)
              f.close()
            print(f'ssl config for {project.name} - generated')

        if project.https == 'openssl':
          if os.path.isdir(f'/webcrate/openssl/{project.name}'):
            with open(f'/webcrate/ssl.conf', 'r') as f:
              conf = f.read()
              f.close()
            conf = conf.replace('%type%', 'openssl')
            conf = conf.replace('%path%', f'{project.name}')
            with open(f'/webcrate/nginx/ssl/{project.name}.conf', 'w') as f:
              f.write(conf)
              f.close()
            print(f'ssl config for {project.name} - generated')

        with open(f'/webcrate/dnsmasq/hosts/{project.name}.hosts', 'w') as f:
          f.write(f'{DOCKER_HOST_IP} {" ".join(project.domains)}\n')
          f.close()

    with open(f'/webcrate/meta/{projectname}.jsonDump', 'w') as f:
      f.write(dump)
      f.close()
    hash_object = hashlib.sha256(dump.encode())
    hex_dig = hash_object.hexdigest()
    os.system(f'printf "{hex_dig}" > /webcrate/meta/{projectname}.checksum')

os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/meta')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/nginx')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/php_pools')
os.system(f'chown -R {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/dnsmasq')
sys.stdout.flush()
