#!/bin/bash

sed -i "s/# primary_hostname =/primary_hostname = $EXIM_PRIMARY_HOSTNAME/g" /etc/mail/exim.conf

/sitesbox/generate_configs.sh
/sitesbox/generate_hosts.sh
dnsmasq --server=$SITESBOX_EXTERNAL_DNS_IP -d &
systemctl init
