#!/bin/bash

/generate_configs.sh
/generate_hosts.sh
dnsmasq --server=$SITESBOX_EXTERNAL_DNS_IP -d &
systemctl init
