#!/bin/bash

user=$(whoami);

gunicorn_pids=`ps aux | grep gunicorn | grep daemon | grep $user | awk '{ print $2 }'`;
gunicorn_pids_count=`printf "$gunicorn_pids" | wc -l`;

if [[ $gunicorn_pids_count > 1 ]]; then

    if [[ -f ~/tmp/gunicorn.pid ]]; then

      printf "$gunicorn_pids" | grep -f ~/tmp/gunicorn.pid | xargs kill -HUP
      echo HUP signal sent for main gunicorn process

    else

      printf "$gunicorn_pids" | xargs kill -HUP
      echo HUP signal sent for all gunicorn processes

    fi

else
  echo gunicorn process not found. starting new
  if [[ -f "~/$DATA_FOLDER/gunicorn.conf.py" ]] ; then
    CONFIG=" -c ~/$DATA_FOLDER/gunicorn.conf.py"
  fi
  gunicorn --daemon --bind :9000 --name $user --user $user --group $user --pid ~/tmp/gunicorn.pid --error-logfile ~/log/gunicorn-error.log$CONFIG --chdir ~/$DATA_FOLDER core.wsgi:application
fi
