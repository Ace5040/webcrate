#!/bin/bash
echo "export WEBCRATE_PROJECT=$WEBCRATE_PROJECT" >> env.bash
echo "export WEBCRATE_DOMAIN=$WEBCRATE_DOMAIN" >> env.bash
cp /etc/mail/exim.conf.template /etc/exim/exim.conf
sed -i "s/%PROJECTDOMAIN%/$WEBCRATE_DOMAIN/g" /etc/exim/exim.conf;
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/exim/exim.conf;
chown root:root /etc/exim/exim.conf
cp /webcrate/supervisord-user.conf.template /etc/supervisord-user.conf
cp /webcrate/supervisord.conf.template /etc/supervisord.conf
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/supervisord-user.conf;
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/supervisord.conf;
chmod a+r /etc/supervisord-user.conf
/webcrate/sync_ssh_keys.sh
cp /webcrate/pools/$WEBCRATE_PROJECT.conf /etc/php81/php-fpm.d/$WEBCRATE_PROJECT.conf
sed -i "s/;error_log = log\/php81\/error.log/error_log = \/home\/$WEBCRATE_PROJECT\/log\/php-fpm-error.log/g" /etc/php81/php-fpm.conf && \
/webcrate/parse-projects.py
/usr/bin/supervisord -c /etc/supervisord.conf
