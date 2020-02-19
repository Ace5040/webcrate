#!/bin/bash

u=${1};
user=$u;
path=$u;
group=$u;
pool=$u;

u_exist=`grep -c "^$u:" /etc/passwd`;

if [[ $MODE == "DEV" || $u_exist == 0 ]]; then
    user='dev';
    group='dev';
fi;

port=${2};

if [[ -f /sitesbox/sites_configs/$u.conf ]]; then

    gunicorn_data=`cat /sitesbox/sites_configs/$u.conf | grep '#gunicorn'`;
    gunicorn=${gunicorn_data//#gunicorn};

    if [[ $gunicorn != '' ]]; then

      source /sites/$path/app/env/bin/activate
      sudo -u $user gunicorn --daemon --bind :$port --name $path --user $user --group $group --pid ../tmp/gunicorn.pid --error-logfile ../logs/gunicorn-error.log -c /sites/$path/app/gunicorn.conf.py --chdir /sites/$path/app core.wsgi:application
      deactivate

    fi

fi
