#!/bin/bash

if [ "$WEBCRATE_APP_MODE" == "DEV" ]; then
  cd /app
  sudo -u app composer install --no-scripts
  cd /app/assets/admin
  sudo -u app npm install
  sudo -u app npm run build
fi

/webcrate/init-db.py

exec systemctl init
