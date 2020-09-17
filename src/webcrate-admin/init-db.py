#!/usr/bin/env python3

import os
import yaml
import time
from munch import munchify
from pprint import pprint

with open('/webcrate/services.yml', 'r') as f:
  services = munchify(yaml.safe_load(f))
  f.close()

WEBCRATE_MODE = os.environ.get('WEBCRATE_MODE', 'DEV')
WEBCRATE_ADMIN_EMAIL = os.environ.get('WEBCRATE_ADMIN_EMAIL', 'email@notset')
WEBCRATE_UID = os.environ.get('WEBCRATE_UID', '1000')
WEBCRATE_GID = os.environ.get('WEBCRATE_GID', '1000')

mysql_service_password=os.popen("cat /webcrate/secrets/webcrate-service-mysql.txt | grep password= | awk '{split($0,a,\"password=\"); print a[2]}' | tr -d \"\n\"").read().strip()
webcrate_secret=os.popen("cat /webcrate/secrets/webcrate-admin.secret | grep secret= | awk '{split($0,a,\"secret=\"); print a[2]}' | tr -d \"\n\"").read().strip()

with open(f'/app/.env.local', 'w') as f:
  f.write('APP_ENV=dev\n')
  f.write(f'APP_SECRET={webcrate_secret}\n')
  f.write(f'DATABASE_URL=mysql://webcrate:{mysql_service_password}@mysql:3306/webcrate\n')
  f.close()

mysql_database_found = int(os.popen(f'mysql -u webcrate -h mysql -p"{mysql_service_password}" -e "show databases like \'webcrate\';" | grep "Database (webcrate)" | wc -l').read().strip())
if mysql_database_found != 0:
  os.system(f'cd /app; php bin/console doctrine:migrations:sync-metadata-storage')
  os.system(f'cd /app; php bin/console doctrine:migrations:migrate')
  admin_user_found = int(os.popen(f'mysql -u webcrate -h mysql -p"{mysql_service_password}" webcrate -e "select id from user where id=1" | wc -l').read().strip())
  if admin_user_found == 0:
    admin_password=os.popen("cat /webcrate/secrets/webcrate-admin.secret | grep password= | awk '{split($0,a,\"password=\"); print a[2]}' | tr -d \"\n\"").read().strip()
    admin_password_encoded=os.popen(f'cd /app; php bin/console security:encode-password "{admin_password}" | grep "Encoded password" | awk \'{{split($0,a,"password"); print a[2]}}\' | tr -d " \n"').read().strip()
    admin_password_encoded = str(admin_password_encoded).replace("$", "\$")
    os.system(f'mysql -u webcrate -h mysql -p"{mysql_service_password}" webcrate -e "INSERT INTO \\`user\\` (\\`id\\`, \\`email\\`, \\`roles\\`, \\`password\\`) VALUES (NULL, \'{WEBCRATE_ADMIN_EMAIL}\', \'[\\"ROLE_ADMIN\\"]\', \'{admin_password_encoded}\')"')
    print(f'webcrate admin user created')
  else:
    print(f'webcrate admin user exists')
else:
  print(f'webcrate database not found')

os.system(f'cd /app; composer run-script post-install-cmd')
