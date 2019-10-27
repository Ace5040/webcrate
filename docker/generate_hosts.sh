#!/bin/bash

#clean up hosts
rm /dnsmasq_hosts/*

if [[ $MODE == "DEV" ]]; then
    echo -n > /dnsmasq_hosts/hosts_nginx
    for i in /nginx_configs/*.conf; do
        [ -f "$i" ] || break
        names_string=`cat $i | grep server_name`
        names_string_clean=${names_string//;}
        names_only_string=${names_string_clean//server_name }
        echo $DOCKER_HOST_IP $names_only_string >> /dnsmasq_hosts/hosts_nginx
    done
fi
