#!/usr/bin/env python3

import os
import yaml
import time
from munch import munchify
from pprint import pprint

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_ADMIN_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', 'email@notset')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

def is_mysql_up(host, password):
  return int(os.popen(f'mysql -u root -h {host} -p"{password}" -e "show databases;" | grep "Database" | wc -l').read().strip())

mysql_root_password = os.popen(f'cat /webcrate/secrets/mysql.cnf | grep "password="').read().strip().split("password=")[1][1:][:-1].replace("$", "\$")
retries = 20
retries2 = 20
while retries > 0 and is_mysql_up('mysql', mysql_root_password) == 0:
  retries -= 1
  time.sleep(5)
if retries > 0:
  while retries2 > 0 and not os.path.isfile(f'/webcrate/secrets/webcrate-admin-service-mysql.txt'):
    retries2 -= 1
    time.sleep(5)
  if retries2 > 0:
    mysql_service_password=os.popen("cat /webcrate/secrets/webcrate-admin-service-mysql.txt | grep password= | awk '{split($0,a,\"password=\"); print a[2]}' | tr -d \"\n\"").read().strip()
    webcrate_secret=os.popen("cat /webcrate/secrets/webcrate-admin.secret | grep secret= | awk '{split($0,a,\"secret=\"); print a[2]}' | tr -d \"\n\"").read().strip()
    with open(f'/app/.env.local', 'w') as f:
      f.write('APP_ENV=dev\n')
      f.write(f'APP_SECRET={webcrate_secret}\n')
      f.write(f'DATABASE_URL=mysql://webcrate-admin:{mysql_service_password}@mysql:3306/webcrate-admin\n')
      f.close()
    mysql_database_found = int(os.popen(f'mysql -u webcrate-admin -h mysql -p"{mysql_service_password}" -e "show databases like \'webcrate-admin\';" | grep "Database (webcrate-admin)" | wc -l').read().strip())
    if mysql_database_found != 0:
      os.system(f'cd /app; php bin/console doctrine:migrations:sync-metadata-storage')
      os.system(f'cd /app; yes | php bin/console doctrine:migrations:migrate')
      admin_user_found = int(os.popen(f'mysql -u webcrate-admin -h mysql -p"{mysql_service_password}" webcrate-admin -e "select id from user where id=1" | wc -l').read().strip())
      if admin_user_found == 0:
        admin_password=os.popen("cat /webcrate/secrets/webcrate-admin.secret | grep password= | awk '{split($0,a,\"password=\"); print a[2]}' | tr -d \"\n\"").read().strip()
        admin_password_encoded=os.popen(f'cd /app; php bin/console security:encode-password "{admin_password}" | grep "Encoded password" | awk \'{{split($0,a,"password"); print a[2]}}\' | tr -d " \n"').read().strip()
        admin_password_encoded = str(admin_password_encoded).replace("$", "\$").replace("&", "\&")
        os.system(f'mysql -u webcrate-admin -h mysql -p"{mysql_service_password}" webcrate-admin -e "INSERT INTO \\`user\\` (\\`id\\`, \\`email\\`, \\`roles\\`, \\`password\\`) VALUES (NULL, \'{WEBCRATE_ADMIN_EMAIL}\', \'[\\"ROLE_ADMIN\\"]\', \'{admin_password_encoded}\')"')
        print(f'webcrate admin user created')
      else:
        print(f'webcrate admin user exists')
      os.system(f'cd /app; php bin/console cache:pool:clear cache.app')
    else:
      print(f'webcrate database not found')
    os.system(f'cd /app; composer run-script post-install-cmd')
  else:
    print(f'webcrate admin secret not generated')
else:
  print(f'mysql is down?')
