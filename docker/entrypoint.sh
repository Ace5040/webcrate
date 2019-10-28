#!/bin/bash

/sitesbox/generate_configs.sh
/sitesbox/generate_hosts.sh
dnsmasq --server=$SITESBOX_EXTERNAL_DNS_IP -d &
systemctl init
