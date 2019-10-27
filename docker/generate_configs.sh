#!/bin/bash

port=9000;
SITES_PATH=/sites

#clean up configs
rm /nginx_configs/*
rm /etc/php/php-fpm.d/*
rm /etc/php56/php-fpm.d/*


#generate production mode pools

if [[ $MODE == "PRODUCTION" ]]; then

    usermod -s /bin/false dev

    for shadow_data in $(cut -d: -f1,2 /shadow_host); do
        u=`cut -d: -f1 <<< $shadow_data`;
        p=`cut -d: -f2 <<< $shadow_data`;
        if [[ $p != '!!' && $p != '' && $u != 'root' ]]; then
            for passwd_data in $(cut -d: -f1,3 /passwd_host); do
                pu=`cut -d: -f1 <<< $passwd_data`;
                if [[ $pu == $u && -d "$SITES_PATH/$u" ]]; then
                  uid=`cut -d: -f2 <<< $passwd_data`;
                  u_exist=`grep -c "^$u:" /etc/passwd`;
                  if [[ $u_exist == 0 ]]; then
                    useradd --no-create-home --uid $uid --home-dir $SITES_PATH/$u $u
                  fi
                  usermod -p "$p" $u;
                  /generate_pool.sh $u $port
                  port=$(($port + 1));
                fi
            done
        fi
    done

fi

#generate pools for dev mode

if [[ $MODE == "DEV" ]]; then

    echo -e "$DEV_MODE_USER_PASS\n$DEV_MODE_USER_PASS" | passwd dev
    usermod -u $DEV_MODE_USER_UID dev
    groupmod -g $DEV_MODE_USER_GID dev

    for i in /sites_configs/*.conf; do
        [ -f "$i" ] || continue
	filename=$(basename -- "$i")
        user="${filename%.*}"

        if [[ -d "$SITES_PATH/$user" ]]; then
    	    /generate_pool.sh $user $port
            port=$(($port + 1));
        fi

    done

fi

#parse custom configs for both modes (phpmyadmin etc.)

for i in /sites_configs/*.conf; do
    [ -f "$i" ] || continue
    filename=$(basename -- "$i")
    user="${filename%.*}"
    if [[ ! -d "$SITES_PATH/$user" ]]; then
        /generate_pool.sh $user $port
        port=$(($port + 1));
    fi
done
