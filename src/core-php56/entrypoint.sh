#!/bin/bash

echo "export WEBCRATE_PROJECT=$WEBCRATE_PROJECT" >> env.bash
echo "set -x WEBCRATE_PROJECT $WEBCRATE_PROJECT" >> env.fish
echo "export WEBCRATE_DOMAIN=$WEBCRATE_DOMAIN" >> env.bash
echo "set -x WEBCRATE_DOMAIN $WEBCRATE_DOMAIN" >> env.fish
cp /etc/mail/exim.conf.template /etc/mail/exim.conf
sed -i "s/# primary_hostname =/primary_hostname = $WEBCRATE_DOMAIN/g"  /etc/mail/exim.conf;
chown root:root /etc/mail/exim.conf
/webcrate/sync_ssh_keys.sh
mkdir -p /etc/php56/php-fpm.d
cp /webcrate/pools/$WEBCRATE_PROJECT.conf /etc/php56/php-fpm.d/$WEBCRATE_PROJECT.conf
/webcrate/parse-projects.py
exec systemctl init
