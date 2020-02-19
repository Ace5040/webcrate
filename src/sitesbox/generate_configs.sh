#!/bin/bash

port=9000;
SITES_PATH=/sites

#production mode

if [[ $MODE == "PRODUCTION" ]]; then

    usermod -s /bin/false dev > /dev/null 2>&1

    for shadow_data in $(cut -d: -f1,2 /sitesbox/shadow); do
        u=`cut -d: -f1 <<< $shadow_data`
        p=`cut -d: -f2 <<< $shadow_data`
        if [[ $p != '!!' && $p != '' && $u != 'root' ]]; then
            for passwd_data in $(cut -d: -f1,3 /sitesbox/passwd); do
                pu=`cut -d: -f1 <<< $passwd_data`
                if [[ $pu == $u && -d "$SITES_PATH/$u" ]]; then
                  chmod o-x $SITES_PATH/$u
                  uid=`cut -d: -f2 <<< $passwd_data`
                  u_exist=`grep -c "^$u:" /etc/passwd`
                  if [[ $u_exist == 0 ]]; then
                    useradd --no-create-home --uid $uid --home-dir $SITES_PATH/$u $u
                  fi
                  usermod -p "$p" $u > /dev/null 2>&1
                  /sitesbox/gunicorn_init.sh $u $port
                  port=$(($port + 1));
                fi
            done
        fi
    done

fi

#dev mode

if [[ $MODE == "DEV" ]]; then

    usermod -p "$DEV_MODE_USER_PASS" dev > /dev/null 2>&1
    usermod -u $DEV_MODE_USER_UID dev > /dev/null 2>&1
    groupmod -g $DEV_MODE_USER_GID dev > /dev/null 2>&1

    for i in /sitesbox/sites_configs/*.conf; do
      [ -f "$i" ] || continue
      filename=$(basename -- "$i")
      user="${filename%.*}"

      if [[ -d "$SITES_PATH/$user" ]]; then
        chmod o-x $SITES_PATH/$user
        /sitesbox/gunicorn_init.sh $user $port
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
        /sitesbox/gunicorn_init.sh $user $port
        port=$(($port + 1));
    fi
done
