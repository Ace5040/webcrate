#!/bin/bash

user=$(whoami);

gunicorn_pids=`ps aux | grep gunicorn | grep daemon | grep $user | awk '{ print $2 }'`;
gunicorn_pids_count=`printf "$gunicorn_pids" | wc -l`;

if [[ $gunicorn_pids_count > 1 ]]; then

    if [[ -f /sites/$user/tmp/gunicorn.pid ]]; then

      printf "$gunicorn_pids" | grep -f /sites/$user/tmp/gunicorn.pid | xargs kill -HUP
      echo HUP signal sent for main gunicorn process

    else

      printf "$gunicorn_pids" | xargs kill -HUP
      echo HUP signal sent for all gunicorn processes

    fi

else

    echo gunicorn process not found

fi
