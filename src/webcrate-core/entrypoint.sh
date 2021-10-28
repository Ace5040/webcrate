#!/bin/bash

echo "export WEBCRATE_MODE=$WEBCRATE_MODE" >> env.bash
echo "set -x WEBCRATE_MODE $WEBCRATE_MODE" >> env.fish
cp /etc/mail/exim.original.conf /etc/mail/exim.conf
chown root:root /etc/mail/exim.conf
/webcrate/sync_ssh_keys.sh
/webcrate/parse-projects.py
echo server=$WEBCRATE_EXTERNAL_DNS_IP >> /etc/dnsmasq.conf
exec systemctl init
