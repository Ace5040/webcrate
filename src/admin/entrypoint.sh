#!/bin/bash

if [ $WEBCRATE_UID != '0' ]; then
  usermod -u $WEBCRATE_UID app > /dev/null 2>&1
  chown $WEBCRATE_UID /webcrate > /dev/null 2>&1
fi

if [ $WEBCRATE_GID != '0' ]; then
  groupmod -g $WEBCRATE_GID app > /dev/null 2>&1
  chgrp $WEBCRATE_GID /webcrate > /dev/null 2>&1
fi

/webcrate/init-db.py

exec systemctl init
