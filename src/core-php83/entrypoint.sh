#!/bin/bash
echo "export WEBCRATE_PROJECT=$WEBCRATE_PROJECT" >> env.bash
echo "export WEBCRATE_DOMAIN=$WEBCRATE_DOMAIN" >> env.bash
cp /etc/mail/exim.conf.template /etc/exim/exim.conf
sed -i "s/%PROJECTDOMAIN%/$WEBCRATE_DOMAIN/g" /etc/exim/exim.conf;
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/exim/exim.conf;
chown root:root /etc/exim/exim.conf
# cp /webcrate/supervisord.conf.template /etc/supervisord.conf
# sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/supervisord.conf;
# chown root:root /etc/supervisord.conf
# chmod a+r /etc/supervisord.conf
# /webcrate/sync_ssh_keys.sh
# cp /webcrate/pools/$WEBCRATE_PROJECT.conf /etc/php81/php-fpm.d/$WEBCRATE_PROJECT.conf
# /webcrate/parse-projects.py
# exec systemctl init
/usr/bin/supervisord -c /etc/supervisord.conf
