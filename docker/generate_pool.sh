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

    php_version_data=`cat /sitesbox/sites_configs/$u.conf | grep '#php'`;
    php=${php_version_data//#php};

    gunicorn_data=`cat /sitesbox/sites_configs/$u.conf | grep '#gunicorn'`;
    gunicorn=${gunicorn_data//#gunicorn};

    if [[ $gunicorn == '' ]]; then

      if [[ $php == '' ]]; then
        php='7';
      fi

      if [[ $php == '7' ]]; then
        php_path_prefix='';
      fi

      if [[ $php == '73' ]]; then
        php_path_prefix='73';
      fi

      if [[ $php == '5' ]]; then
        php_path_prefix='56';
      fi

      if [[ -f /sitesbox/custom_templates/$u.conf ]]; then
        template_path=/sitesbox/custom_templates/$u.conf
      else
        template_path="/sitesbox/custom_templates/php$php-default.conf"
      fi

      cp -rf $template_path /etc/php$php_path_prefix/php-fpm.d/$u.conf

      sed -i -- "s/%port%/$port/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
      sed -i -- "s/%user%/$user/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
      sed -i -- "s/%path%/$path/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
      sed -i -- "s/%group%/$group/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
      sed -i -- "s/%pool%/$pool/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf

      test -d /sites/$path && echo "alias php='/bin/php$php_path_prefix'" > /sites/$path/phpversion.sh
      test -d /sites/$path && echo "alias composer='php /bin/composer'" >> /sites/$path/phpversion.sh

    else

      source /sites/$path/app/env/bin/activate
      sudo -u $user gunicorn --daemon --bind :$port --name $path --user $user --group $group --pid ../tmp/gunicorn.pid --error-logfile ../logs/gunicorn-error.log -c /sites/$path/app/gunicorn.conf.py --chdir /sites/$path/app core.wsgi:application
      deactivate

    fi

    cp -rf /sitesbox/sites_configs/$u.conf /sitesbox/nginx_configs/$u.conf
    sed -i -- "s/%port%/$port/g" /sitesbox/nginx_configs/$u.conf
    sed -i -- "s/%user%/$u/g" /sitesbox/nginx_configs/$u.conf
    sed -i -- "s/%PHPMYADMIN_DNS_NAME%/$PHPMYADMIN_DNS_NAME/g" /sitesbox/nginx_configs/$u.conf

fi
