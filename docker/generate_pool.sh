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

if [[ -f /sites_configs/$u.conf ]]; then

    php_version_data=`cat /sites_configs/$u.conf | grep '#php'`;
    php=${php_version_data//#php};

    if [[ $php == '' ]]; then
        php='7';
    fi

    if [[ $php == '5' ]]; then
        php_path_prefix='56';
    else
        php_path_prefix='';
    fi;

    if [[ -f /custom_templates/$u.conf ]]; then
        template_path=/custom_templates/$u.conf
    else
        template_path="/custom_templates/php$php-default.conf"
    fi

    cp -rf $template_path /etc/php$php_path_prefix/php-fpm.d/$u.conf

    sed -i -- "s/%port%/$port/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
    sed -i -- "s/%user%/$user/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
    sed -i -- "s/%path%/$path/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
    sed -i -- "s/%group%/$group/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf
    sed -i -- "s/%pool%/$pool/g" /etc/php$php_path_prefix/php-fpm.d/$u.conf

    cp -rf /sites_configs/$u.conf /nginx_configs/$u.conf
    sed -i -- "s/%port%/$port/g" /nginx_configs/$u.conf
    sed -i -- "s/%user%/$u/g" /nginx_configs/$u.conf

fi
