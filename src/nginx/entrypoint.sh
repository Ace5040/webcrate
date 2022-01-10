#!/bin/bash

sed -i "s/error_log  \/var\/log\/nginx\/error.log notice/error_log  \/dev\/null crit/g" /etc/nginx/nginx.conf
sed -i "s/access_log  \/var\/log\/nginx\/access.log  main/access_log  off/g" /etc/nginx/nginx.conf
sed -i "s/#gzip  on/include \/webcrate\/nginx-config\/\*\.conf/g" /etc/nginx/nginx.conf

if [[ $WEBCRATE_UID == 0 ]] ; then
    gpasswd -a nginx root
    exec nginx -g 'daemon off;'
else
    groupadd --gid $WEBCRATE_GID dev
    gpasswd -a nginx dev
    usermod -u $WEBCRATE_UID nginx
    usermod -g $WEBCRATE_GID nginx
    chown -R nginx:nginx /var/log/nginx
    chown -R nginx:nginx /var/cache/nginx
    chown -R nginx:nginx /run
    rm /var/log/nginx/error.log
    exec sudo -u nginx nginx -g 'daemon off;'
fi
