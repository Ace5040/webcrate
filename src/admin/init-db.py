#!/usr/bin/env python3

import os
import time

WEBCRATE_PROJECTS_FOLDERS = os.environ.get('WEBCRATE_PROJECTS_FOLDERS', 'var/projects')
WEBCRATE_ADMIN_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', 'email@notset')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

def is_mysql_up(host, password):
  return int(os.popen(f'mariadb --skip-ssl -u root -h {host} -p"{password}" -e "show databases;" | grep "Database" | wc -l').read().strip())

mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\\$")
retries = 20
retries2 = 20
while retries > 0 and is_mysql_up('webcrate-admin-mysql', mysql_root_password) == 0:
  retries -= 1
  time.sleep(5)
if retries > 0:
  while retries2 > 0 and not os.path.isfile(f'/webcrate/secrets/admin-service-mysql.txt'):
    retries2 -= 1
    time.sleep(5)
  if retries2 > 0:
    mysql_service_password=os.popen("cat /webcrate/secrets/admin-service-mysql.txt | grep password= | awk '{split($0,a,\"password=\"); print a[2]}' | tr -d \"\n\"").read().strip()
    webcrate_secret=os.popen("cat /webcrate/secrets/admin.secret | grep secret= | awk '{split($0,a,\"secret=\"); print a[2]}' | tr -d \"\n\"").read().strip()
    with open(f'/app/.env.local', 'w') as f:
      f.write('APP_ENV=dev\n')
      f.write(f'APP_SECRET={webcrate_secret}\n')
      f.write(f'WEBCRATE_UID={WEBCRATE_UID}\n')
      f.write(f'WEBCRATE_GID={WEBCRATE_GID}\n')
      f.write(f'WEBCRATE_PROJECTS_FOLDERS={WEBCRATE_PROJECTS_FOLDERS}\n')
      f.write(f'DATABASE_URL=mysql://admin:{mysql_service_password}@webcrate-admin-mysql:3306/admin\n')
      f.close()
    mysql_database_found = int(os.popen(f'mariadb --skip-ssl -u admin -h webcrate-admin-mysql -p"{mysql_service_password}" -e "show databases like \'admin\';" | grep "Database (admin)" | wc -l').read().strip())
    if mysql_database_found != 0:
      os.system(f'cd /app; php bin/console doctrine:migrations:sync-metadata-storage')
      os.system(f'cd /app; yes | php bin/console doctrine:migrations:migrate')
      admin_user_found = int(os.popen(f'mariadb --skip-ssl -u admin -h webcrate-admin-mysql -p"{mysql_service_password}" admin -e "select id from user where id=1" | wc -l').read().strip())
      if admin_user_found == 0:
        admin_password=os.popen("cat /webcrate/secrets/admin.secret | grep password= | awk '{split($0,a,\"password=\"); print a[2]}' | tr -d \"\n\"").read().strip()
        admin_password_encoded=os.popen(f'cd /app; php bin/console security:encode-password "{admin_password}" | grep "Encoded password" | awk \'{{split($0,a,"password"); print a[2]}}\' | tr -d " \n"').read().strip()
        admin_password_encoded = str(admin_password_encoded).replace("$", "\\$").replace("&", "\\&")
        os.system(f'mariadb --skip-ssl -u admin -h webcrate-admin-mysql -p"{mysql_service_password}" admin -e "INSERT INTO \\`user\\` (\\`id\\`, \\`email\\`, \\`roles\\`, \\`password\\`) VALUES (NULL, \'{WEBCRATE_ADMIN_EMAIL}\', \'[\\"ROLE_ADMIN\\"]\', \'{admin_password_encoded}\')"')
        print(f'admin user created')
      else:
        print(f'admin user exists')
      os.system(f'cd /app; php bin/console doctrine:fixtures:load --group=Backends --group=HttpsTypes --group=NginxTemplates --append')
      os.system(f'cd /app; php bin/console cache:pool:clear cache.app')
    else:
      print(f'database not found')
    os.system(f'cd /app; composer run-script post-install-cmd')
  else:
    print(f'admin secret not generated')
else:
  print(f'mariadb is down')
