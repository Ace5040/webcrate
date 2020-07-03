#!/bin/bash

/sitesbox/sync_ssh_keys.sh
/sitesbox/generate_configs.sh
dnsmasq --server=$SITESBOX_EXTERNAL_DNS_IP -d &
systemctl init
