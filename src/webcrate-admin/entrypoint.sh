#!/bin/bash

if [ $WEBCRATE_UID != '0' ]; then
  usermod -u $WEBCRATE_UID app > /dev/null 2>&1
  chown $WEBCRATE_UID /webcrate > /dev/null 2>&1
  chown -R $WEBCRATE_UID /app > /dev/null 2>&1
fi

if [ $WEBCRATE_GID != '0' ]; then
  groupmod -g $WEBCRATE_GID app > /dev/null 2>&1
  chgrp $WEBCRATE_GID /webcrate > /dev/null 2>&1
  chgrp -R $WEBCRATE_GID /app > /dev/null 2>&1
fi

if [ "$WEBCRATE_APP_MODE" == "DEV" ]; then
  cd /app
  sudo -u app composer install --no-scripts
  cd /app/assets/admin
  sudo -u app npm install
  sudo -u app npm run build
fi

/webcrate/init-db.py

exec systemctl init
