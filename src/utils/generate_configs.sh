#!/bin/bash

port=9000;
SITES_PATH=/sites

#clean up configs
rm /sitesbox/nginx_configs/*
rm /sitesbox/php-fpm.d/*
rm /sitesbox/php73-fpm.d/*
rm /sitesbox/php56-fpm.d/*

#generate production mode pools

if [[ $SITESBOX_MODE == "PRODUCTION" ]]; then

    usermod -s /bin/false dev > /dev/null 2>&1

    for shadow_data in $(cut -d: -f1,2 /sitesbox/shadow); do
        u=`cut -d: -f1 <<< $shadow_data`
        p=`cut -d: -f2 <<< $shadow_data`
        if [[ $p != '!!' && $p != '' && $u != 'root' ]]; then
            for passwd_data in $(cut -d: -f1,3 /sitesbox/passwd); do
                pu=`cut -d: -f1 <<< $passwd_data`
                if [[ $pu == $u && -d "$SITES_PATH/$u" ]]; then
                  uid=`cut -d: -f2 <<< $passwd_data`
                  u_exist=`grep -c "^$u:" /etc/passwd`
                  if [[ $u_exist == 0 ]]; then
                    useradd --no-create-home --uid $uid --home-dir $SITES_PATH/$u $u
                  fi
                  usermod -p "$p" $u > /dev/null 2>&1
                  /sitesbox/generate_pool.sh $u $port
                  port=$(($0port + 1))
                fi
            done
        fi
    done

fi

#generate pools for dev mode

if [[ $SITESBOX_MODE == "DEV" ]]; then

    usermod -u $DEV_MODE_USER_UID dev /dev/null 2>&1
    groupmod -g $DEV_MODE_USER_GID dev /dev/null 2>&1

    for i in /sitesbox/sites_configs/*.conf; do
      [ -f "$i" ] || continue
      filename=$(basename -- "$i")
      user="${filename%.*}"

      if [[ -d "$SITES_PATH/$user" ]]; then
        /sitesbox/generate_pool.sh $user $port
        port=$(($port + 1));
      fi

    done

fi

#parse custom configs for both modes (phpmyadmin etc.)

for i in /sitesbox/sites_configs/*.conf; do
    [ -f "$i" ] || continue
    filename=$(basename -- "$i")
    user="${filename%.*}"
    if [[ ! -d "$SITES_PATH/$user" ]]; then
        /sitesbox/generate_pool.sh $user $port
        port=$(($port + 1));
    fi
done
