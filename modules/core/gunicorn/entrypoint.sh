#!/bin/bash
echo "export WEBCRATE_PROJECT=$WEBCRATE_PROJECT" >> env.bash
echo "export WEBCRATE_DOMAIN=$WEBCRATE_DOMAIN" >> env.bash
cp /etc/mail/exim.conf.template /etc/exim4/exim.conf
sed -i "s/%PROJECTDOMAIN%/$WEBCRATE_DOMAIN/g" /etc/exim4/exim.conf;
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/exim4/exim.conf;
chown root:root /etc/exim4/exim.conf
cp /webcrate/supervisord-user.conf.template /etc/supervisord-user.conf
cp /webcrate/supervisord.conf.template /etc/supervisord.conf
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/supervisord-user.conf;
sed -i "s/%USERNAME%/$WEBCRATE_PROJECT/g" /etc/supervisord.conf;
chmod a+r /etc/supervisord-user.conf
/webcrate/sync_ssh_keys.sh
sed -i '1s/^/. \/etc\/bashrc.sh\n/' /etc/bash.bashrc
sed -i '1s/^/. \/etc\/default\/locale\n/' /etc/bash.bashrc
sed -i '1s/^/export USER=${USER:-$(id -u -n)}\n/' /etc/bash.bashrc
echo LANG=C.utf8 >> /etc/default/locale
echo LANGUAGE=C.utf8 >> /etc/default/locale
echo LC_ALL=C.utf8 >> /etc/default/locale
/webcrate/parse-projects.py
/usr/bin/supervisord -c /etc/supervisord.conf
