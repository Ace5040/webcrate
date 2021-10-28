FROM archlinux:latest

#update pacman db
RUN pacman --needed --noconfirm -Syu

#install system utils and services
RUN pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients dnsmasq mc iputils cronie inetutils which ruby python-pip python-virtualenv wget tmux fish

#install latest php
RUN pacman --needed --noconfirm -S php php-fpm php-intl php-sqlite php-gd php-xsl php-tidy php-imagick php-memcached xdebug

#add dev user
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev

#grant dev user sudo priviledges
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo

#enable 6 cores support for make
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev

#install yay
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR /home/dev/yay
RUN makepkg -scir --noconfirm
WORKDIR /home/dev

#remove yay src
RUN rm -rf /home/dev/yay

#install php 74
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S php74 php74-fpm php74-intl php74-sqlite php74-gd php74-xsl php74-tidy php74-imagick php74-memcached php74-xdebug
RUN yay --noconfirm -R msmtp-mta

#install php 73
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S php73 php73-fpm php73-intl php73-sqlite php73-gd php73-xsl php73-tidy php73-imagick php73-memcached php73-xdebug

#install php 56
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S php56 php56-fpm php56-intl php56-sqlite php56-gd php56-xsl php56-tidy php56-imagick php56-memcached
RUN git clone https://aur.archlinux.org/php56-xdebug.git
WORKDIR /home/dev/php56-xdebug
RUN sed -i '31,38d;51d' PKGBUILD
RUN makepkg -scir --noconfirm
WORKDIR /home/dev
RUN rm -rf /home/dev/php56-xdebug

#install soft from aur
RUN yay --gpgflags "--keyserver hkp://keyserver.ubuntu.com" --noeditmenu --nodiffmenu --noconfirm --mflags --nocheck -S docker-systemctl-replacement-git symfony-cli telegraf-bin proftpd composer1 vue-cli
#python38

USER root

#install drush
RUN wget -O drush.phar https://github.com/drush-ops/drush-launcher/releases/latest/download/drush.phar; \
    chmod +x drush.phar; \
    mv drush.phar /usr/bin/drush

#install legacy drush
RUN wget -O drush.0.8.0.phar https://github.com/drush-ops/drush-launcher/releases/download/0.8.0/drush.phar; \
    chmod +x drush.0.8.0.phar; \
    mv drush.0.8.0.phar /usr/bin/drush.0.8.0

#install compass
RUN gem install compass --norc

#install phyton libs
RUN pip install pyyml munch

#replace postfix with exim
RUN pacman --noconfirm -R postfix
RUN pacman --needed --noconfirm -S exim

RUN chown root:root /bin/systemctl.py
RUN chmod a+x /bin/systemctl.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl.py /bin/systemctl
RUN ssh-keygen -A
RUN systemctl enable php-fpm; \
    systemctl enable php74-fpm; \
    systemctl enable php73-fpm; \
    systemctl enable php56-fpm; \
    systemctl enable sshd; \
    systemctl enable cronie; \
    systemctl enable telegraf; \
    systemctl enable exim; \
    systemctl enable dnsmasq; \
    systemctl enable proftpd

RUN printf "\ninclude=/etc/php56/php-fpm.d/*.conf" >> /etc/php56/php-fpm.conf; \
    sed -i "s/Type=dbus/Type=simple/g" /usr/lib/systemd/system/dnsmasq.service; \
    sed -i "s/--enable-dbus //g" /usr/lib/systemd/system/dnsmasq.service; \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php/php-fpm.conf; \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php74/php-fpm.conf; \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php73/php-fpm.conf; \
    sed -i "s/;process_control_timeout = 0/process_control_timeout = 10s/g"  /etc/php56/php-fpm.conf; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php74/php.ini; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php73/php.ini; \
    sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php56/php.ini; \
    sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf; \
    sed -i "s/#PubkeyAuthentication yes/PubkeyAuthentication yes/g" /etc/ssh/sshd_config;
WORKDIR /
COPY proftpd.conf /etc/proftpd.conf
RUN printf "no-resolv\nno-poll\nno-hosts\naddn-hosts=/webcrate-dnsmasq/config/hosts_nginx\n" > /etc/dnsmasq.conf
RUN echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc
RUN echo 'dev ALL=(ALL) NOPASSWD: /bin/crontab' | EDITOR='tee -a' visudo
RUN sed -i 's/test -r /test -e /g' /etc/profile
RUN mkdir -p /webcrate; \
    mkdir -p /webcrate-bin; \
    mkdir -p /webcrate-bin/php; \
    mkdir -p /webcrate-bin/php74; \
    mkdir -p /webcrate-bin/php73; \
    mkdir -p /webcrate-bin/php56; \
    ln -s /bin/php /webcrate-bin/php/php; \
    ln -s /bin/php74 /webcrate-bin/php74/php; \
    ln -s /bin/php73 /webcrate-bin/php73/php; \
    ln -s /bin/php56 /webcrate-bin/php56/php; \
    ln -s /bin/drush.0.8.0 /webcrate-bin/php56/drush; \
    mkdir -p /webcrate-fish; \
    chmod o-rwx /webcrate
WORKDIR /webcrate-fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish
WORKDIR /webcrate-fish/oh-my-fish
RUN bin/install --offline --path=/webcrate-fish/omf --noninteractive --config=/webcrate-fish/omfconf; \
    cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish; \
    fish -C "omf install cbjohnson"; \
    cp /webcrate-fish/omf/themes/default/functions/fish_right_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_right_prompt.fish;
COPY fish_prompt.fish /webcrate-fish/omf/themes/cbjohnson/fish_prompt.fish
WORKDIR /root
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz; \
    tar xzvf ioncube_loaders_lin_x86-64.tar.gz; \
    cp ioncube/ioncube_loader_lin_7.4.so /usr/lib/php74/modules/ioncube_loader_lin.so; \
    cp ioncube/ioncube_loader_lin_7.3.so /usr/lib/php73/modules/ioncube_loader_lin.so; \
    cp ioncube/ioncube_loader_lin_5.6.so /usr/lib/php56/modules/ioncube_loader_lin.so; \
    rm /etc/php/conf.d/imagick.ini; \
    rm /etc/php74/conf.d/imagick.ini; \
    rm /etc/php73/conf.d/imagick.ini; \
    rm /etc/php56/conf.d/imagick.ini; \
    rm /etc/php/conf.d/xdebug.ini; \
    rm /etc/php74/conf.d/xdebug.ini; \
    rm /etc/php73/conf.d/xdebug.ini; \
    rm /etc/php56/conf.d/xdebug.ini; \
    yes | sudo symfony self-update

#remove ioncube files
RUN rm -rf /root/ioncube
RUN rm -f /root/ioncube_loaders_lin_x86-64.tar.gz

WORKDIR /
RUN mkdir -p /webcrate-telegraf; \
    chown telegraf:telegraf /webcrate-telegraf; \
    chmod o-rwx /webcrate-telegraf; \
    mkdir -p /webcrate-dnsmasq; \
    chown dnsmasq:dnsmasq /webcrate-dnsmasq; \
    chmod o-rwx /webcrate-dnsmasq

COPY ["toprc", "/etc/telegraf/.config/procps/"]
COPY ["fishrc.fish", "/etc/fish/conf.d/"]
COPY ["bashrc.sh", "/etc/profile.d/"]
COPY ["stats_projects.sh", "stats_pools.sh", "/webcrate-telegraf/"]
COPY ["gunicorn_restart.sh", "/webcrate-bin/"]
COPY ["reload.py", "versions.py", "parse-projects.py", "sync_ssh_keys.sh", "log.py", "/webcrate/"]
COPY ["entrypoint.sh", "/"]

RUN chmod u+x /webcrate/sync_ssh_keys.sh; \
    chmod a+x /webcrate-telegraf/stats_projects.sh; \
    chmod a+x /webcrate-telegraf/stats_pools.sh; \
    mkdir -p /etc/telegraf/.config/procps; \
    rm /etc/mail/exim.conf; \
    chmod a+x /webcrate-bin/gunicorn_restart.sh; \
    chmod u+x /webcrate/parse-projects.py; \
    chmod u+x /webcrate/reload.py; \
    chmod u+x /webcrate/versions.py; \
    chmod u+x /entrypoint.sh
CMD ["/entrypoint.sh"]
