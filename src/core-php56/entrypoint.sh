#!/bin/bash

echo "export WEBCRATE_MODE=$WEBCRATE_MODE" >> env.bash
echo "set -x WEBCRATE_MODE $WEBCRATE_MODE" >> env.fish
echo "export WEBCRATE_PROJECT=$WEBCRATE_PROJECT" >> env.bash
echo "set -x WEBCRATE_PROJECT $WEBCRATE_PROJECT" >> env.fish
cp /etc/mail/exim.original.conf /etc/mail/exim.conf
chown root:root /etc/mail/exim.conf
/webcrate/sync_ssh_keys.sh
/webcrate/parse-projects.py
exec systemctl init
