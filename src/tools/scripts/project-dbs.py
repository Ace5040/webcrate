#!/usr/bin/env python3

import os
import sys
import yaml
import time
from munch import munchify
import helpers

WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

with open('/webcrate/projects.yml', 'r') as f:
  projects = munchify(yaml.safe_load(f))
  f.close()

PROJECT_NAME = sys.argv[1]

for projectname,project in projects.items():
  project.name = projectname
  if PROJECT_NAME == project.name:
    if project.active:
      if hasattr(project, 'volume'):
        project.folder = f'/projects{(project.volume + 1) if project.volume else ""}/{project.name}'
      else:
        project.folder = f'/projects/{project.name}'
      if project.mysql_db:
        mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
        retries = 20
        while retries > 0 and helpers.is_mysql_up('webcrate-mysql', mysql_root_password) == 0:
          retries -= 1
          time.sleep(5)
        if retries > 0:
          mysql_database_found = int(os.popen(f'mysql -u root -h webcrate-mysql -p"{mysql_root_password}" -e "show databases like \'{project.name}\';" | grep "Database ({project.name})" | wc -l').read().strip())
          if mysql_database_found == 0:
            mysql_user_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
            with open(f'/webcrate/secrets/{project.name}-mysql.txt', 'w') as f:
              f.write(f'host=webcrate-mysql\n')
              f.write(f'name={project.name}\n')
              f.write(f'user={project.name}\n')
              f.write(f'password={mysql_user_password}\n')
              f.close()
            os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{project.name}-mysql.txt')
            os.system(f'cp /webcrate/secrets/{project.name}-mysql.txt {project.folder}/mysql.txt')
            os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/mysql.txt')
            os.system(f'chmod a-rwx,u+rw {project.folder}/mysql.txt')
            os.system(f'mysql -u root -h webcrate-mysql -p"{mysql_root_password}" -e "CREATE DATABASE \`{project.name}\`;"')
            os.system(f"mysql -u root -h webcrate-mysql -p\"{mysql_root_password}\" -e \"CREATE USER \`{project.name}\`@'%' IDENTIFIED BY \\\"{mysql_user_password}\\\";\"")
            os.system(f"mysql -u root -h webcrate-mysql -p\"{mysql_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{project.name}\` . * TO \`{project.name}\`@'%';\"")
            os.system(f"mysql -u root -h webcrate-mysql -p\"{mysql_root_password}\" -e \"FLUSH PRIVILEGES;\"")
            print(f'mysql user {project.name} and db created')
          else:
            print(f'mysql user {project.name} and db already exists')
      if project.mysql5_db:
        mysql5_root_password = os.popen(f'cat /webcrate/secrets/mysql5.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
        retries = 20
        while retries > 0 and helpers.is_mysql_up('webcrate-mysql5', mysql5_root_password) == 0:
          retries -= 1
          time.sleep(5)
        if retries > 0:
          mysql5_database_found = int(os.popen(f'mysql -u root -h webcrate-mysql5 -p"{mysql5_root_password}" -e "show databases like \'{project.name}\';" | grep "Database ({project.name})" | wc -l').read().strip())
          if mysql5_database_found == 0:
            mysql5_user_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
            with open(f'/webcrate/secrets/{project.name}-mysql5.txt', 'w') as f:
              f.write(f'host=webcrate-mysql\n')
              f.write(f'db={project.name}\n')
              f.write(f'user={project.name}\n')
              f.write(f'password={mysql5_user_password}\n')
              f.close()
            os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{project.name}-mysql5.txt')
            os.system(f'cp /webcrate/secrets/{project.name}-mysql5.txt {project.folder}/mysql5.txt')
            os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/mysql5.txt')
            os.system(f'chmod a-rwx,u+rw {project.folder}/mysql5.txt')
            os.system(f'mysql -u root -h webcrate-mysql5 -p"{mysql5_root_password}" -e "CREATE DATABASE \`{project.name}\`;"')
            os.system(f"mysql -u root -h webcrate-mysql5 -p\"{mysql5_root_password}\" -e \"CREATE USER \`{project.name}\`@'%' IDENTIFIED BY \\\"{mysql5_user_password}\\\";\"")
            os.system(f"mysql -u root -h webcrate-mysql5 -p\"{mysql5_root_password}\" -e \"GRANT ALL PRIVILEGES ON \`{project.name}\` . * TO \`{project.name}\`@'%';\"")
            os.system(f"mysql -u root -h webcrate-mysql5 -p\"{mysql5_root_password}\" -e \"FLUSH PRIVILEGES;\"")
            print(f'mysql5 user {project.name} and db created')
          else:
            print(f'mysql5 user {project.name} and db already exists')
      if project.postgresql_db:
        postgres_root_password = os.popen(f'cat /webcrate/secrets/postgres.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
        retries = 20
        while retries > 0 and helpers.is_postgresql_up('webcrate-postgres', postgres_root_password) != '1':
          retries -= 1
          time.sleep(5)
        if retries > 0:
          postgres_database_found = os.popen(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "SELECT 1 FROM pg_database WHERE datname=\'{project.name}\';"').read().strip()
          if postgres_database_found != '1':
            postgres_user_password=os.popen(f"/webcrate/pwgen.sh").read().strip()
            with open(f'/webcrate/secrets/{project.name}-postgres.txt', 'w') as f:
              f.write(f'host=webcrate-postgres\n')
              f.write(f'db={project.name}\n')
              f.write(f'user={project.name}\n')
              f.write(f'password={postgres_user_password}\n')
              f.close()
            os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} /webcrate/secrets/{project.name}-postgres.txt')
            os.system(f'cp /webcrate/secrets/{project.name}-postgres.txt {project.folder}/postgres.txt')
            os.system(f'chown {WEBCRATE_UID}:{WEBCRATE_GID} {project.folder}/postgres.txt')
            os.system(f'chmod a-rwx,u+rw {project.folder}/postgres.txt')
            os.system(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "CREATE DATABASE {project.name};"')
            os.system(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "CREATE USER {project.name} WITH ENCRYPTED PASSWORD \'{postgres_user_password}\';"')
            os.system(f'psql -d "host=webcrate-postgres user=postgres password={postgres_root_password}" -tAc "GRANT ALL PRIVILEGES ON DATABASE {project.name} TO {project.name};"')
            print(f'postgresql user {project.name} and db created')
          else:
            print(f'postgresql user {project.name} and db already exists')
