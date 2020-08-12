#!/bin/bash

/webcrate/sync_ssh_keys.sh
/webcrate/parse-users.py
dnsmasq --server=$WEBCRATE_EXTERNAL_DNS_IP -d &
systemctl init
