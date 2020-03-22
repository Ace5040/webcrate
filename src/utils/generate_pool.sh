#!/bin/bash

u=${1};
user=$u;
path=$u;
group=$u;
pool=$u;

u_exist=`grep -c "^$u:" /etc/passwd`;

if [[ $SITESBOX_MODE == "DEV" || $u_exist == 0 ]]; then
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

      cp -rf $template_path /sitesbox/php$php_path_prefix-fpm.d/$u.conf

      sed -i -- "s/%port%/$port/g" /sitesbox/php$php_path_prefix-fpm.d/$u.conf
      sed -i -- "s/%user%/$user/g" /sitesbox/php$php_path_prefix-fpm.d/$u.conf
      sed -i -- "s/%path%/$path/g" /sitesbox/php$php_path_prefix-fpm.d/$u.conf
      sed -i -- "s/%group%/$group/g" /sitesbox/php$php_path_prefix-fpm.d/$u.conf
      sed -i -- "s/%pool%/$pool/g" /sitesbox/php$php_path_prefix-fpm.d/$u.conf

      test -d /sites/$path && echo "PATH=/sitesbox/bin/php$php_path_prefix:\$PATH" > /sites/$path/phpversion.sh
      test -d /sites/$path && echo "set PATH /sitesbox/bin/php$php_path_prefix \$PATH" > /sites/$path/phpversion.fish
    fi

    cp -rf /sitesbox/sites_configs/$u.conf /sitesbox/nginx_configs/$u.conf
    sed -i -- "s/%port%/$port/g" /sitesbox/nginx_configs/$u.conf
    sed -i -- "s/%user%/$u/g" /sitesbox/nginx_configs/$u.conf
    sed -i -- "s/%PHPMYADMIN_DNS_NAME%/$PHPMYADMIN_DNS_NAME/g" /sitesbox/nginx_configs/$u.conf

fi
