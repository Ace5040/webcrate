#!/bin/bash

sed -i "s/\/var\/log\/nginx\/error.log/\/dev\/null/g" /etc/nginx/nginx.conf
sed -i "s/\/var\/log\/nginx\/access.log/off/g" /etc/nginx/nginx.conf
sed -i "s/#gzip  on/include \/webcrate\/nginx-config\/\*\.conf/g" /etc/nginx/nginx.conf
/webcrate/parse-projects.py

if [[ $WEBCRATE_UID == 0 ]] ; then
    exec nginx -g 'daemon off;'
else
    usermod -u $WEBCRATE_UID nginx
    usermod -g $WEBCRATE_GID nginx
    chown -R nginx:nginx /var/log/nginx
    chown -R nginx:nginx /var/cache/nginx
    chown -R nginx:nginx /run
    rm /var/log/nginx/error.log
    exec sudo -u nginx nginx -g 'daemon off;'
fi
