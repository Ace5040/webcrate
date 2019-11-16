FROM archlinux/base
RUN pacman --noconfirm -Syu
RUN pacman --noconfirm -S mc nano git unzip sudo fakeroot binutils awk autoconf pkgconf bison gcc patch exim dnsmasq php php-fpm php-gd php-xsl php-intl php-tidy php-imagick composer npm python2 mariadb-clients openssh make
RUN useradd -m -s /bin/bash dev
RUN usermod -p "dev" dev
RUN echo 'dev ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo
USER dev
WORKDIR /home/dev
RUN git clone https://aur.archlinux.org/aurman.git
WORKDIR /home/dev/aurman
RUN gpg --recv-key 465022E743D71E39
RUN makepkg -scir --noconfirm
RUN aurman --noedit --skip_news --skip_new_locations --noconfirm -S docker-systemctl-replacement-git
USER root
RUN chown root:root /bin/systemctl3.py
RUN chmod a+x /bin/systemctl3.py
RUN mv /bin/systemctl /bin/systemctl_original
RUN cp /bin/systemctl3.py /bin/systemctl
RUN printf "#!/bin/sh\npkgconf \"\$\@\" freetype2\n" > /usr/bin/freetype-config
RUN chmod +x /usr/bin/freetype-config
USER dev
RUN gpg --recv-key 6E4F6AB321FDC07F2C332E3AC2BF0BC433CFC8B3
RUN gpg --recv-key 0BD78B5F97500D450838F95DFE857D9A90D90EC1
RUN aurman --noedit --skip_news --skip_new_locations --noconfirm -S php56 php56-fpm php56-gd php56-xsl php56-intl php56-tidy php56-imagick
RUN aurman --noedit --skip_news --skip_new_locations --noconfirm -S drush-launcher
USER root
RUN printf "\ninclude=/etc/php56/php-fpm.d/*.conf" >> /etc/php56/php-fpm.conf
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php/php.ini
RUN sed -i "s/.*open_basedir =.*/open_basedir =/g" /etc/php56/php.ini
RUN sed -i "s/;extension=imagick/extension=imagick/g" /etc/php/conf.d/imagick.ini
RUN pacman --noconfirm -S iputils
RUN ssh-keygen -A
RUN systemctl enable php-fpm
RUN systemctl enable php56-fpm
RUN systemctl enable sshd
RUN curl https://drupalconsole.com/installer -L -o drupal.phar
RUN mv drupal.phar /bin/drupal
RUN chmod a+x /bin/drupal
USER dev
RUN aurman --noedit --skip_news --skip_new_locations --noconfirm -S telegraf-bin
USER root
RUN sed -i "s/# urls = \[\"http\:\/\/127\.0\.0\.1\:8086\"\]/urls = \[\"http\:\/\/influxdb\:8086\"\]/g" /etc/telegraf/telegraf.conf
RUN sed -i "s/# skip_database_creation = false/skip_database_creation = true/g" /etc/telegraf/telegraf.conf
RUN sed -i "s/# database = \"telegraf\"/database = \"telegraf\"/g" /etc/telegraf/telegraf.conf
RUN systemctl enable telegraf
RUN pacman --noconfirm -S cronie
RUN systemctl enable cronie
RUN pacman --noconfirm -S inetutils which
RUN pacman --noconfirm -S ruby
RUN gem install compass --norc
WORKDIR /
RUN printf "no-resolv\nno-poll\nno-hosts\naddn-hosts=/sitesbox/dnsmasq_hosts/hosts_nginx\n" > /etc/dnsmasq.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh
RUN mkdir -p /sitesbox
COPY generate_configs.sh /sitesbox/generate_configs.sh
RUN chmod u+x /sitesbox/generate_configs.sh
COPY generate_hosts.sh /sitesbox/generate_hosts.sh
RUN chmod u+x /sitesbox/generate_hosts.sh
COPY generate_pool.sh /sitesbox/generate_pool.sh
RUN chmod u+x /sitesbox/generate_pool.sh
COPY stats_users.sh /sitesbox/stats_users.sh
RUN chmod a+x /sitesbox/stats_users.sh
COPY stats_pools.sh /sitesbox/stats_pools.sh
RUN chmod a+x /sitesbox/stats_pools.sh
RUN mkdir -p /etc/telegraf/.config/procps
RUN rm /etc/mail/exim.conf
COPY sitesbox_profile.sh /etc/profile.d/sitesbox_profile.sh
COPY toprc /etc/telegraf/.config/procps/toprc
CMD ["/entrypoint.sh"]
