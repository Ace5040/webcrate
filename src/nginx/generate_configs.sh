#!/bin/bash

if [[ $SITESBOX_MODE == "PRODUCTION" ]]; then

    for group_data in $(cut -d: -f1,3 /sitesbox/group); do
        g=`cut -d: -f1 <<< $group_data`;
        if [[ -d "$SITES_PATH/$g" ]]; then
          gid=`cut -d: -f2 <<< $group_data`;
          g_exist=`grep -c "^$g:" /etc/group`;
          if [[ $g_exist == 0 ]]; then
            groupadd --gid $gid $g
          fi
          gpasswd -a nginx $g
        fi
    done

fi

#dev mode

if [[ $SITESBOX_MODE == "DEV" ]]; then

    groupadd --gid $DEV_MODE_USER_GID dev
    gpasswd -a nginx dev

fi
