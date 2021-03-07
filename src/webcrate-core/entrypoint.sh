#!/bin/bash

echo "export WEBCRATE_MODE=$WEBCRATE_MODE" >> env.bash
echo "set -x WEBCRATE_MODE $WEBCRATE_MODE" >> env.fish
/webcrate/sync_ssh_keys.sh
/webcrate/parse-users.py
echo server=$WEBCRATE_EXTERNAL_DNS_IP >> /etc/dnsmasq.conf
sed -i "s/Type=dbus/Type=simple/g" /usr/lib/systemd/system/dnsmasq.service
sed -i "s/--enable-dbus //g" /usr/lib/systemd/system/dnsmasq.service
exec systemctl init
