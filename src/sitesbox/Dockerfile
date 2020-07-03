FROM archlinux:latest
RUN echo "Set disable_coredump false" >> /etc/sudo.conf
RUN pacman --noconfirm -Syu
RUN pacman --needed --noconfirm -S git nano openssh base-devel unzip composer npm mariadb-clients dnsmasq mc iputils cronie inetutils which ruby python-virtualenv
RUN pacman --needed --noconfirm -S php php-fpm php-gd php-xsl php-intl php-tidy php-imagick php-memcached
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
RUN sed -i "s/#MAKEFLAGS=\"-j2\"/MAKEFLAGS=\"-j6\"/g" /etc/makepkg.conf
USER dev
WORKDIR /home/dev
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR /home/dev/yay
RUN makepkg -scir --noconfirm
WORKDIR /home/dev
RUN yay --noeditmenu --nodiffmenu -S docker-systemctl-replacement-git
RUN yay --noeditmenu --nodiffmenu --noconfirm -S --mflags --nocheck php73 php73-fpm php73-gd php73-xsl php73-intl php73-tidy
RUN yay --noeditmenu --nodiffmenu --noconfirm -S php73-imagick php73-memcached
RUN gpg --recv-key C2BF0BC433CFC8B3
RUN yay --noeditmenu --nodiffmenu --noconfirm -S --mflags --nocheck php56 php56-fpm php56-gd php56-xsl php56-intl php56-tidy
RUN yay --noeditmenu --nodiffmenu --noconfirm -S --mflags --nocheck php56-imagick php56-memcached
RUN yay --noeditmenu --nodiffmenu --noconfirm -S drush-launcher telegraf-bin pip-tools tmux fish
RUN yay --noeditmenu --nodiffmenu --noconfirm -S xdebug php73-xdebug
RUN yay --noeditmenu --nodiffmenu --noconfirm -S php-intl php73-intl php56-intl
RUN yay --noeditmenu --nodiffmenu --noconfirm -S symfony-cli
USER root
RUN pacman --noconfirm -R postfix
RUN pacman --noconfirm -S exim
RUN chown root:root /bin/systemctl.py
RUN chmod a+x /bin/systemctl.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl.py /bin/systemctl
RUN ssh-keygen -A
RUN systemctl enable php-fpm
RUN systemctl enable php73-fpm
RUN systemctl enable php56-fpm
RUN systemctl enable sshd
RUN systemctl enable cronie
RUN systemctl enable telegraf
RUN systemctl enable exim
RUN printf "\ninclude=/etc/php56/php-fpm.d/*.conf" >> /etc/php56/php-fpm.conf
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php73/php.ini
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php56/php.ini
RUN sed -i "s/;extension=imagick/extension=imagick/g" /etc/php/conf.d/imagick.ini
RUN sed -i "s/;extension=imagick/extension=imagick/g" /etc/php73/conf.d/imagick.ini
RUN sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf
RUN sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf
RUN sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf
RUN sed -i 's/  interval = "10s"/  interval = "1s"/g' /etc/telegraf/telegraf.conf
RUN gem install compass --norc
WORKDIR /
RUN printf "no-resolv\nno-poll\nno-hosts\naddn-hosts=/sitesbox/dnsmasq_hosts/hosts_nginx\n" > /etc/dnsmasq.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
RUN mkdir -p /sitesbox
RUN mkdir -p /sitesbox/bin
COPY generate_configs.sh /sitesbox/generate_configs.sh
RUN chmod u+x /sitesbox/generate_configs.sh
COPY gunicorn_init.sh /sitesbox/gunicorn_init.sh
RUN chmod u+x /sitesbox/gunicorn_init.sh
COPY stats_users.sh /sitesbox/stats_users.sh
RUN chmod a+x /sitesbox/stats_users.sh
COPY stats_pools.sh /sitesbox/stats_pools.sh
RUN chmod a+x /sitesbox/stats_pools.sh
RUN mkdir -p /etc/telegraf/.config/procps
RUN rm /etc/mail/exim.conf
COPY bashrc.sh /etc/profile.d/bashrc.sh
COPY fishrc.fish /etc/fish/conf.d/fishrc.fish
COPY toprc /etc/telegraf/.config/procps/toprc
COPY gunicorn_restart.sh /sitesbox/bin/gunicorn_restart.sh
RUN chmod a+x /sitesbox/bin/gunicorn_restart.sh
RUN echo ". /etc/profile.d/bashrc.sh" >> /etc/bash.bashrc
RUN mkdir -p /sitesbox/bin/php
RUN mkdir -p /sitesbox/bin/php73
RUN mkdir -p /sitesbox/bin/php56
RUN ln -s /bin/php /sitesbox/bin/php/php
RUN ln -s /bin/php73 /sitesbox/bin/php73/php
RUN ln -s /bin/php56 /sitesbox/bin/php56/php
RUN mkdir -p /sitesbox/fish
WORKDIR /sitesbox/fish
RUN git clone https://github.com/oh-my-fish/oh-my-fish
WORKDIR /sitesbox/fish/oh-my-fish
RUN bin/install --offline --path=/sitesbox/fish/omf --config=/sitesbox/fish/omfconf
RUN cp /root/.config/fish/conf.d/omf.fish /etc/fish/conf.d/omf.fish
RUN fish -C "omf install cbjohnson"
RUN cp /sitesbox/fish/omf/themes/default/fish_right_prompt.fish /sitesbox/fish/omf/themes/cbjohnson/fish_right_prompt.fish
COPY fish_prompt.fish /sitesbox/fish/omf/themes/cbjohnson/fish_prompt.fish
WORKDIR /root
RUN pacman -S --needed --noconfirm wget
RUN wget https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz
RUN wget https://www.ioncube.com/php-7.4.0-beta-loaders/ioncube_loaders_lin_x86-64_7.4_BETA2.tar.gz
RUN tar xzvf ioncube_loaders_lin_x86-64.tar.gz
RUN tar xzvf ioncube_loaders_lin_x86-64_7.4_BETA2.tar.gz
RUN cp ioncube/ioncube_loader_lin_5.6.so /usr/lib/php56/modules/ioncube_loader_lin.so
RUN cp ioncube/ioncube_loader_lin_7.3.so /usr/lib/php73/modules/ioncube_loader_lin.so
RUN cp ioncube_loader_lin_7.4_10.4.0_beta2.so /usr/lib/php/modules/ioncube_loader_lin.so
RUN rm /etc/php73/conf.d/xdebug.ini
#USER dev
#RUN yay --noeditmenu --nodiffmenu --noconfirm -S proftpd
#USER root
#COPY proftpd.conf /etc/proftpd.conf
#RUN systemctl enable proftpd
WORKDIR /sitesbox
CMD ["/entrypoint.sh"]
