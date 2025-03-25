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

if ! [ -e "/webcrate/log/admin.supervisor.log" ] ; then
  touch /webcrate/log/admin.supervisor.log
fi
sudo chown $WEBCRATE_UID:$WEBCRATE_GID /webcrate/log/admin.supervisor.log
cp /webcrate/supervisord.conf.template /tmp/supervisord.conf
sudo /usr/bin/supervisord -c /tmp/supervisord.conf
